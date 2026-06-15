"""
Tartib — Telegram Bot
Vazifalarni vaqtida eslatib turadi.

O'rnatish:
  pip install python-telegram-bot==21.* apscheduler==3.* django requests python-decouple

Ishga tushirish:
  python telegram_bot/bot.py

.env da quyidagilarni qo'shing:
  TELEGRAM_BOT_TOKEN=123456:ABC-your-token
  MINI_APP_URL=https://your-tartib-site.com
  TARTIB_API_URL=http://localhost:8000/api
"""

import os
import sys
import logging
import django
import requests
import asyncio
import urllib.parse
from datetime import datetime, date, timedelta

# Django setup — bot loyiha papkasidan ishlaydi
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tartib.settings')
django.setup()

from decouple import config
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler


def make_link_button(text: str, url: str) -> InlineKeyboardButton:
    """Return a Web App button for HTTPS URLs, otherwise fall back to a normal URL button."""
    if url.startswith('https://'):
        return InlineKeyboardButton(text=text, web_app=WebAppInfo(url=url))
    return InlineKeyboardButton(text=text, url=url)


def build_web_app_url(base_url: str, **params) -> str:
    if not params:
        return base_url
    separator = '&' if '?' in base_url else '?'
    return f"{base_url}{separator}{urllib.parse.urlencode(params)}"

from apps.authentication.models import User
from apps.tasks.models import Task

# ─── Config ───────────────────────────────────────────────────────────────────

BOT_TOKEN   = config('TELEGRAM_BOT_TOKEN')
MINI_APP_URL = config('MINI_APP_URL', default='https://tartib.com.uz')

logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(message)s',
    level=logging.INFO
)
log = logging.getLogger(__name__)

PRIORITY_EMOJI = {
    'danger': '🔴',
    'amber':  '🟡',
    'gray':   '⚪',
}

# ─── /start ───────────────────────────────────────────────────────────────────

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchini qabul qiladi va Mini Appni ochish tugmasini ko'rsatadi."""
    user = update.effective_user

    keyboard = InlineKeyboardMarkup([[make_link_button('📋 Tartibni ochish', build_web_app_url(MINI_APP_URL, telegramId=user.id))]])

    await update.message.reply_text(
        f"Salom, {user.first_name}! 👋\n\n"
        f"Men <b>Tartib</b> botiman. Vazifalaringiz vaqti kelganda sizni ogohlantiraman.\n\n"
        f"Eslatmalar olish uchun Tartib ilovangizda <b>Telegram ID</b>ingizni ulang.\n"
        f"Sizning Telegram ID: <code>{user.id}</code>\n\n"
        f"Quyidagi tugma orqali ilovani oching:",
        parse_mode='HTML',
        reply_markup=keyboard
    )

# ─── /help ────────────────────────────────────────────────────────────────────

async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 <b>Buyruqlar:</b>\n\n"
        "/start — botni ishga tushirish\n"
        "/bugun — bugungi vazifalar\n"
        "/ertaga — ertangi vazifalar\n"
        "/id — Telegram ID ni ko'rish\n\n"
        "Eslatmalar avtomatik keladi — hech narsa qilish shart emas.",
        parse_mode='HTML'
    )

# ─── /id ──────────────────────────────────────────────────────────────────────

async def show_id(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(
        f"🆔 Telegram ID: <code>{uid}</code>\n\n"
        f"Bu ID ni Tartib ilovasidagi Sozlamalar bo'limiga kiriting.",
        parse_mode='HTML'
    )

# ─── /bugun ───────────────────────────────────────────────────────────────────

async def today_tasks(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    await send_task_list(update.message, tg_id, date.today(), 'Bugungi')

# ─── /ertaga ──────────────────────────────────────────────────────────────────

async def tomorrow_tasks(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    await send_task_list(update.message, tg_id, date.today() + timedelta(days=1), 'Ertangi')

# ─── Task ro'yxatini yuborish ─────────────────────────────────────────────────

async def send_task_list(message, tg_id: int, target_date: date, label: str):
    try:
        user = User.objects.get(telegram_id=tg_id)
    except User.DoesNotExist:
        await message.reply_text(
            "❌ Tartib akkauntingiz topilmadi.\n\n"
            "Sozlamalar bo'limida Telegram ID ingizni ulang.",
            parse_mode='HTML'
        )
        return

    tasks = Task.objects.filter(
        user=user, date=target_date, done=False
    ).order_by('time', '-created_at')

    if not tasks.exists():
        await message.reply_text(f"✅ {label} bajariladigan vazifalar yo'q!")
        return

    lines = [f"📋 <b>{label} vazifalar ({target_date.strftime('%d.%m.%Y')}):</b>\n"]
    for t in tasks:
        em = PRIORITY_EMOJI.get(t.pri, '⚪')
        time_str = f" — {t.time}" if t.time else ""
        cat_str  = f" [{t.category.name}]" if t.category else ""
        lines.append(f"{em} {t.title}{time_str}{cat_str}")

    keyboard = InlineKeyboardMarkup([[make_link_button('📋 Ilovani ochish', MINI_APP_URL)]])

    await message.reply_text(
        '\n'.join(lines),
        parse_mode='HTML',
        reply_markup=keyboard
    )

# ─── Eslatma yuborish (scheduler tomonidan chaqiriladi) ───────────────────────

async def send_reminders(app: Application):
    """
    Har daqiqada ishga tushadi.
    Hozirgi vaqtga mos kelgan vazifalarni topib, foydalanuvchilariga yuboradi.
    """
    now = datetime.now()
    current_time = now.strftime('%H:%M')
    today = now.date()

    tasks = Task.objects.filter(
        date=today,
        time=current_time,
        done=False,
        user__telegram_id__isnull=False
    ).select_related('user', 'category')

    for task in tasks:
        tg_id = task.user.telegram_id
        if not tg_id:
            continue

        em = PRIORITY_EMOJI.get(task.pri, '⚪')
        cat_str = f"\n🏷 {task.category.name}" if task.category else ""
        text = (
            f"⏰ <b>Vazifa vaqti keldi!</b>\n\n"
            f"{em} <b>{task.title}</b>\n"
            f"🕐 {task.time}{cat_str}\n\n"
            f"Bajarildi deb belgilash uchun ilovani oching."
        )

        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton('📋 Ilovani ochish', web_app=WebAppInfo(url=MINI_APP_URL))
        ]])

        try:
            await app.bot.send_message(
                chat_id=tg_id,
                text=text,
                parse_mode='HTML',
                reply_markup=keyboard
            )
            log.info(f"Eslatma yuborildi: user={task.user.email}, task='{task.title}'")
        except Exception as e:
            log.warning(f"Yuborishda xato (tg_id={tg_id}): {e}")

# ─── Kunlik xulosa (har kuni soat 08:00) ──────────────────────────────────────

async def send_morning_summary(app: Application):
    """Har kuni ertalab bugungi vazifalar sonini yuboradi."""
    today = date.today()

    users = User.objects.filter(
        telegram_id__isnull=False
    ).exclude(telegram_id=0)

    for user in users:
        tasks = Task.objects.filter(user=user, date=today, done=False)
        count = tasks.count()
        if count == 0:
            continue

        urgent = tasks.filter(pri='danger').count()
        text = (
            f"🌅 <b>Xayrli tong!</b>\n\n"
            f"Bugun <b>{count} ta</b> vazifangiz bor"
            + (f", shundan <b>{urgent} tasi muhim</b> 🔴" if urgent else "")
            + ".\n\nKuni samarali o'tsin! 💪"
        )

        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton('📋 Vazifalarni ko\'rish', web_app=WebAppInfo(url=MINI_APP_URL))
        ]])

        try:
            await app.bot.send_message(
                chat_id=user.telegram_id,
                text=text,
                parse_mode='HTML',
                reply_markup=keyboard
            )
        except Exception as e:
            log.warning(f"Xulosa yuborishda xato (user={user.email}): {e}")

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    import signal
    
    app = Application.builder().token(BOT_TOKEN).build()

    # Buyruqlar
    app.add_handler(CommandHandler('start',  start))
    app.add_handler(CommandHandler('help',   help_cmd))
    app.add_handler(CommandHandler('id',     show_id))
    app.add_handler(CommandHandler('bugun',  today_tasks))
    app.add_handler(CommandHandler('ertaga', tomorrow_tasks))

    log.info("Bot ishga tushdi — buyruqlar faol")
    log.info("Eslatmalar va kunlik xulosa soat jadvalsi hozircha o'chirilgan")
    
    # Event loop yaratish (Python 3.10+ uchun)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(app.run_polling(allowed_updates=Update.ALL_TYPES))
    except KeyboardInterrupt:
        log.info("Bot to'xtatildi")
    finally:
        loop.close()


if __name__ == '__main__':
    main()
