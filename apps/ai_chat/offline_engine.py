"""
Offline AI tizimi — hech qanday API kerak emas.
Pattern matching + statistika asosida aqlli javoblar.
"""
from datetime import date, timedelta


class OfflineAIEngine:
    """API keysiz ishlaydi — mahalliy statistika va mantiq asosida."""

    def __init__(self, user):
        self.user = user
        self._load_data()

    def _load_data(self):
        """Foydalanuvchi ma'lumotlarini yuklash."""
        from apps.tasks.models import Task
        from apps.focus.models import FocusSession, UserStreak
        from apps.transactions.models import Transaction

        today = date.today()
        week_start = today - timedelta(days=today.weekday())

        self.today_tasks = list(Task.objects.filter(user=self.user, date=today))
        self.all_tasks = list(Task.objects.filter(user=self.user).order_by('-created_at')[:100])
        self.week_sessions = list(FocusSession.objects.filter(
            user=self.user,
            date__gte=week_start
        ))
        self.streak_obj = UserStreak.objects.filter(user=self.user).first()
        self.month_txs = list(Transaction.objects.filter(
            user=self.user,
            iso_date__gte=date(today.year, today.month, 1)
        ))

        # Hisob-kitoblar
        self.streak = self.streak_obj.count if self.streak_obj else 0
        self.today_done = len([t for t in self.today_tasks if t.done])
        self.today_total = len(self.today_tasks)
        self.week_focus_mins = sum(s.mins for s in self.week_sessions)
        self.month_income = sum(t.amt for t in self.month_txs if t.type == 'income')
        self.month_expense = sum(t.amt for t in self.month_txs if t.type == 'expense')

    def respond(self, message: str) -> str:
        """Xabarga mos javob qaytarish."""
        msg = message.lower().strip()

        # === VAZIFALAR ===
        if any(w in msg for w in ['vazifa', 'task', 'reja', 'nima bor', 'bugun', 'ishlar']):
            return self._tasks_response()

        # === FOCUS / POMODORO ===
        if any(w in msg for w in ['focus', 'pomodoro', 'vaqt', 'soat', 'ishladim', 'samarali']):
            return self._focus_response()

        # === STREAK ===
        if any(w in msg for w in ['streak', 'ketma-ket', 'qancha kun', 'davom']):
            return self._streak_response()

        # === MOLIYA / DAROMAD ===
        if any(w in msg for w in ['daromad', 'pul', 'harajat', 'moliya', 'balans', 'income']):
            return self._finance_response()

        # === MASLAHAT SO'RASH ===
        if any(w in msg for w in ['maslahat', 'tavsiya', 'qanday', 'yaxshi', 'yordam']):
            return self._advice_response()

        # === SALOM / TANISHUV ===
        if any(w in msg for w in ['salom', 'xayrli', 'assalom', 'hi', 'hello']):
            return self._greeting_response()

        # === STATISTIKA ===
        if any(w in msg for w in ['statistika', 'tahlil', "ko'rsatkich", 'natija']):
            return self._stats_response()

        # Default
        return self._general_response(message)

    def _tasks_response(self) -> str:
        pct = round(self.today_done / self.today_total * 100) if self.today_total > 0 else 0

        if self.today_total == 0:
            return (
                "Bugun hali birorta vazifa rejalashtirilmagan. "
                "Samarali kun uchun qisqacha reja tuzing — 3-5 ta asosiy vazifa yetarli. "
                "Muhim vazifalarni ertalab bajaring! 💪"
            )

        pending = self.today_total - self.today_done
        urgent = [t for t in self.today_tasks if not t.done and t.pri == 'danger']

        reply = f"Bugun {self.today_total} ta vazifadan {self.today_done} tasi bajarildi ({pct}%). "

        if urgent:
            reply += f"⚠️ {len(urgent)} ta muhim vazifa hali bajarilmadi: {', '.join(t.title[:20] for t in urgent[:2])}. "

        if pct >= 80:
            reply += "Ajoyib natija! Zo'r ishladingiz! 🎉"
        elif pct >= 50:
            reply += f"Yaxshi boshlanish! {pending} ta vazifa qoldi — davom eting! 💪"
        else:
            reply += "Hali ko'p ish bor. Eng muhim vazifadan boshlang!"

        return reply

    def _focus_response(self) -> str:
        hours = self.week_focus_mins // 60
        mins = self.week_focus_mins % 60

        if self.week_focus_mins == 0:
            return (
                "Bu hafta hali focus seans o'tkazmadingiz. "
                "25 daqiqalik Pomodoro texnikasi bilan boshlang — qisqa, ammo samarali! "
                "Focus tab'ga o'ting va '25 min' tugmasini bosing. 🎯"
            )

        label = f"{hours} soat {mins} daqiqa" if hours > 0 else f"{mins} daqiqa"

        if self.week_focus_mins >= 300:  # 5 soat+
            tip = "Ajoyib hafta! Professional darajada ishlayapsiz! 🏆"
        elif self.week_focus_mins >= 120:
            tip = "Yaxshi natija. Har kuni 25-30 daqiqa qo'shishga harakat qiling."
        else:
            tip = "Boshlang'ich bosqich. Ko'p ahamiyat bermang — muhimi muntazamlik."

        return f"Bu hafta {label} focus vaqt o'tkazdingiz. {tip}"

    def _streak_response(self) -> str:
        if self.streak == 0:
            return "Hali streak yo'q. Bugun bitta focus seans o'tkazing va streakingizni boshlang! 🔥"

        if self.streak >= 30:
            return f"WOW! {self.streak} kunlik streak — bu ixtiyorsiz odat bo'lib qoldi! Siz professional! 🏆🔥"
        elif self.streak >= 7:
            return f"Ajoyib! {self.streak} kunlik streak. Bir hafta+ doimiy ishlayapsiz. Davom eting! 🔥"
        else:
            return f"{self.streak} kunlik streak quryapsiz. Har kuni oz bo'lsa ham focus seans o'tkizing! 🔥"

    def _finance_response(self) -> str:
        net = self.month_income - self.month_expense

        if self.month_income == 0 and self.month_expense == 0:
            return "Bu oyda hali moliyaviy yozuvlar kiritilmagan. Daromad va harajatlarni kuzating — bu katta o'zgarish yaratadi! 💰"

        f = lambda n: f"{n:,}".replace(',', ' ')

        reply = f"Bu oy: daromad {f(self.month_income)} so'm, harajat {f(self.month_expense)} so'm. "

        if net > 0:
            reply += f"Sof balans: +{f(net)} so'm. Tejamkorlik yaxshi! ✅"
        elif net < 0:
            reply += f"Kamomad: -{f(abs(net))} so'm. Harajatlarni ko'rib chiqing. ⚠️"
        else:
            reply += "Daromad va harajat teng. Tejash fondini boshlang!"

        return reply

    def _advice_response(self) -> str:
        import random

        tips = []

        if self.today_total > 0 and self.today_done / self.today_total < 0.5:
            tips.append("Eng muhim 3 ta vazifani aniqlang va faqat shularga e'tibor bering — qolganlarini ertaga qoldiring.")

        if self.week_focus_mins < 60:
            tips.append("Kuniga kamida 25 daqiqa chalg'itishsiz ishlash odatini shakllantiring.")

        if self.streak < 3:
            tips.append("Streak qurishni boshlang — har kuni bitta kichik focus seans yetarli.")

        if self.month_expense > self.month_income:
            tips.append("Harajatlar daromaddan oshib ketmoqda. 50/30/20 qoidasini sinab ko'ring: 50% zaruriyat, 30% istak, 20% tejash.")

        if not tips:
            general = [
                "Ertalab uyg'onib birinchi 90 daqiqani eng muhim ish uchun sarflang.",
                "Har kuni kechqurun ertangi kunning uchta asosiy vazifasini yozing.",
                "Telefon bildirishnomalarini o'chirib, fokus vaqtni himoya qiling.",
                "Pomodoro texnikasida har 4 seans keyin 15 daqiqa uzoq tanaffus qiling.",
            ]
            tips = [random.choice(general)]

        return "💡 Maslahat: " + tips[0]

    def _greeting_response(self) -> str:
        name = self.user.first_name or "Foydalanuvchi"

        if self.today_total == 0:
            return f"Salom, {name}! Bugun uchun reja tuzmadingizmi? Keling, birga rejalashtiraylik! 📋"

        pct = round(self.today_done / self.today_total * 100) if self.today_total > 0 else 0
        return (
            f"Salom, {name}! Bugun {self.today_done}/{self.today_total} vazifa bajarildi ({pct}%). "
            f"Streak: {self.streak} kun 🔥. Davom eting! 💪"
        )

    def _stats_response(self) -> str:
        pct = round(self.today_done / self.today_total * 100) if self.today_total > 0 else 0
        hours = self.week_focus_mins // 60
        mins = self.week_focus_mins % 60
        focus_label = f"{hours}s {mins}d" if hours > 0 else f"{mins} daqiqa"
        net = self.month_income - self.month_expense

        return (
            f"📊 Sizning natijalaringiz:\n"
            f"• Bugun: {self.today_done}/{self.today_total} vazifa ({pct}%)\n"
            f"• Streak: {self.streak} kun 🔥\n"
            f"• Bu hafta focus: {focus_label}\n"
            f"• Bu oy balans: {'+' if net >= 0 else ''}{net:,} so'm"
        )

    def _general_response(self, message: str) -> str:
        return (
            "Sizning so'rovingizni tushundim. Quyidagilar haqida so'rashingiz mumkin: "
            "vazifalar, focus vaqti, streak, daromad/harajat, maslahat, statistika. "
            "Yoki fokus tab'ga o'tib pomodoro sessiyasini boshlang! 🎯"
        )
