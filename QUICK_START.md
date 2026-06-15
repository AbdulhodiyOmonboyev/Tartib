# 🚀 TARTIB - Tezkor Boshlash Qo'llanmasi

## ✅ Hozir Ishga Tushgan

### Backend (Django API) - http://localhost:8000
```bash
cd c:\Users\Abdulxodiy\Desktop\tartib_fixed
.\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
```
**API Endpoints:**
- `/api/tasks/` - Vazifalar
- `/api/transactions/` - Tranzaksiyalar
- `/api/focus/` - Focus sessiyalari
- `/admin/` - Admin panel

### Frontend (React/Vite) - http://localhost:5174
```bash
cd c:\Users\Abdulxodiy\Desktop\tartib_fixed\template
npm run dev
```
**URL:** http://localhost:5174

---

## 🤖 Telegram Bot - Sozlash va Ishga Tushirish

### 1️⃣ Bot Token Olish

1. Telegramda **@BotFather** ga yozing
2. `/newbot` buyrug'ini yuboring
3. Bot nomini kiriting: `Tartib`
4. Bot usernameni kiriting: `tartib_your_bot`
5. **Token olib olingiz** (Example: `123456789:ABCxyz...`)

### 2️⃣ Token .env ga Qo'shing

`c:\Users\Abdulxodiy\Desktop\tartib_fixed\.env` ni oching:

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=123456789:ABCxyz-YOUR-TOKEN-HERE
MINI_APP_URL=http://localhost:5174
TARTIB_API_URL=http://localhost:8000/api
```

### 3️⃣ Telegram Bot ni Ishga Tushirish

```bash
cd c:\Users\Abdulxodiy\Desktop\tartib_fixed
.\venv\Scripts\python.exe telegram_bot/bot.py
```

**Bot Buyruqlari:**
- `/start` - Mini Appni ochish
- `/bugun` - Bugungi vazifalar
- `/ertaga` - Ertangi vazifalar
- `/id` - Telegram ID
- `/help` - Yordam

---

## 📊 Admin Panel

**URL:** http://localhost:8000/admin

Default hisob:
- Username: `admin`
- Password: (yaratishning kerak)

Admin yaratish:
```bash
.\venv\Scripts\python.exe manage.py createsuperuser
```

---

## 🔍 Muammolarni Hal Qilish

### Backend xatosi?
```bash
# Migratsiyalari tekshirish
.\venv\Scripts\python.exe manage.py migrate

# Database reset
del db.sqlite3
.\venv\Scripts\python.exe manage.py migrate
```

### Frontend xatosi?
```bash
# Dependencies o'rnatish
cd template
npm install
npm run dev
```

### Bot xatosi?
- Token to'g'rimi? (.env dan tekshiring)
- Django ishlayaptimi? (Backend 8000 da ishlashi kerak)
- Internet ulanishi bormi? (Telegram API)

---

## 🎯 To'liq Ishga Tushirish (3 Terminal)

**Terminal 1 - Backend:**
```bash
cd c:\Users\Abdulxodiy\Desktop\tartib_fixed
.\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
```

**Terminal 2 - Frontend:**
```bash
cd c:\Users\Abdulxodiy\Desktop\tartib_fixed\template
npm run dev
```

**Terminal 3 - Telegram Bot:** (Token sozlanganidan keyin)
```bash
cd c:\Users\Abdulxodiy\Desktop\tartib_fixed
.\venv\Scripts\python.exe telegram_bot/bot.py
```

---

## 📝 Faylli Yo'llar

```
tartib_fixed/
├── backend/ ............... Django API
├── template/ .............. React Frontend
├── telegram_bot/ ........... Telegram Bot
├── .env .................... Konfiguratsiya
├── db.sqlite3 .............. Database
└── manage.py ............... Django CLI
```

---

## 🎉 Hamma Ishga Tushdi!

- **Frontend:** http://localhost:5174
- **Backend API:** http://localhost:8000
- **Admin Panel:** http://localhost:8000/admin
- **Telegram Bot:** Foydalanuvchilar @BotFather dan topishgan bot

Serverlari to'xtattish: `CTRL + C`
