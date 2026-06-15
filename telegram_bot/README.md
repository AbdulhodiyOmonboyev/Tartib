# Tartib — Telegram Bot sozlash

## 1. O'rnatish

```bash
pip install python-telegram-bot==21.* apscheduler==3.*
```

## 2. Bot yaratish

1. Telegramda @BotFather ga yozing
2. `/newbot` buyrug'ini yuboring
3. Bot nomini kiriting: `Tartib`
4. Bot username kiriting: `tartib_your_bot`
5. Olingan tokenni `.env` ga kiriting

## 3. .env ga qo'shing

```env
TELEGRAM_BOT_TOKEN=123456789:AAF-your-bot-token-here
MINI_APP_URL=https://your-tartib-site.com
```

## 4. Migration

```bash
python manage.py migrate
```

## 5. Botni ishga tushirish

```bash
# Loyiha papkasidan
python telegram_bot/bot.py
```

## 6. Foydalanuvchi ulash

1. Foydalanuvchi botga `/start` yubora → Telegram ID ko'rsatiladi
2. Foydalanuvchi bu ID ni Tartib ilovasidagi Sozlamalar → Telegram ID ga kiriting
3. Shundan keyin eslatmalar avtomatik keladi

---

## Bot imkoniyatlari

| Buyruq | Vazifasi |
|--------|----------|
| `/start` | Mini Appni ochish tugmasi bilan salomlashadi |
| `/bugun` | Bugungi vazifalarni ko'rsatadi |
| `/ertaga` | Ertangi vazifalarni ko'rsatadi |
| `/id` | Telegram ID ni ko'rsatadi |

**Avtomatik:**
- Har daqiqa — hozirgi vaqtga mos vazifalarni eslatadi
- Har kuni soat 08:00 — bugungi vazifalar sonini yuboradi

---

## Production uchun (systemd service)

`/etc/systemd/system/tartib-bot.service`:

```ini
[Unit]
Description=Tartib Telegram Bot
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/tartib
ExecStart=/usr/bin/python3 telegram_bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable tartib-bot
sudo systemctl start tartib-bot
```
