@echo off
REM Telegram Bot Ishga Tushirish
REM Foydalanish: Double-click qiling yoki cmd da run_telegram_bot.cmd

setlocal enabledelayedexpansion
set "BASE_DIR=%~dp0"
if "%BASE_DIR:~-1%"=="\" set "BASE_DIR=%BASE_DIR:~0,-1%"

cd /d "%BASE_DIR%"

echo ========================================
echo   TARTIB Telegram Bot
echo ========================================
echo.

REM .env tekshirish
if not exist ".env" (
    echo XATO: .env fayl topilmadi!
    echo .env faylini yaratib, TELEGRAM_BOT_TOKEN ni kiriting
    pause
    exit /b 1
)

REM Token tekshirish
for /f "tokens=2 delims==" %%A in ('findstr "TELEGRAM_BOT_TOKEN" .env') do set "TOKEN=%%A"
if "%TOKEN%"=="sizning-bot-tokeningiz-bu-yerga" (
    echo XATO: TELEGRAM_BOT_TOKEN hali sozlanmagan!
    echo .env faylini oching va bot tokeningizni kiriting:
    echo TELEGRAM_BOT_TOKEN=123456:ABCxyz...
    echo.
    echo Bot yaratish uchun:
    echo 1. Telegramda @BotFather ga yozing
    echo 2. /newbot buyrug'ini yuboring
    echo 3. Bot nomini va usernameni kiriting
    echo 4. Olingan tokenni .env ga kiriting
    pause
    exit /b 1
)

REM Venv faol qilish
call venv\Scripts\activate.bat

REM Bot kutubxonalarini o'rnatish
echo [1/3] Bot kutubxonalarini o'rnatish...
pip install python-telegram-bot==21.6 apscheduler==3.10.4 -q

REM Django migratsiyalari
echo [2/3] Django migratsiyalarini tekshirish...
python manage.py migrate --noinput -q

REM Bot ishga tushirish
echo [3/3] Bot ishga tushmoqda...
echo.
echo TARTIB Telegram Bot ishga tushdi!
echo Serverni to'xtattish uchun: CTRL + C
echo.

python telegram_bot/bot.py

pause
