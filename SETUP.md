# TARTIB - Loyihani Ishga Tushirish Yo'riqnomasi

Ushbu loyiha Django (Backend) va React/Vite (Frontend) dan iborat. Loyihani ishga tushirishning bir necha yo'li mavjud.

## 1. Avtomatik ishga tushirish (Tavsiya etiladi)
Loyiha ildiz papkasidagi `start.bat` faylini ikki marta bosing. U barcha kutubxonalarni tekshiradi, virtual muhitni yaratadi va ikkala serverni parallel ravishda ishga tushiradi.

---

## 2. Qo'lda (Manual) ishga tushirish
Agar `start.bat` ishlamasa, quyidagi qadamlarni birma-bir bajaring:

### A. Backendni tayyorlash (Django)
1. Terminalni (CMD yoki PowerShell) oching va loyiha papkasiga kiring.
2. Virtual muhitni yarating (agar yo'q bo'lsa):
   ```bash
   python -m venv venv
   ```
3. Virtual muhitni aktivlashtiring:
   * **Windows:** `venv\Scripts\activate`
   * **Mac/Linux:** `source venv/bin/activate`
4. Zarur kutubxonalarni o'rnating:
   ```bash
   pip install -r requirements.txt
   ```
5. Ma'lumotlar bazasini yangilang:
   ```bash
   python manage.py migrate
   ```
6. Backend serverni ishga tushiring:
   ```bash
   python manage.py runserver
   ```
   *Backend manzili: http://localhost:8000*

### B. Frontendni tayyorlash (React/Vite)
1. **Yangi terminal oynasini** oching.
2. `template` papkasiga kiring:
   ```bash
   cd template
   ```
3. Node modulellarini o'rnating (agar yo'q bo'lsa):
   ```bash
   npm install
   ```
4. Frontendni ishga tushiring:
   ```bash
   npm run dev
   ```
   *Frontend manzili: http://localhost:5173 yoki http://localhost:5174*

---

## 3. Mumkin bo'lgan muammolar va yechimlar

*   **"Oppoq oyna" (Blank page):** Brauzer konsolini (F12) tekshiring. Agar API xatosi bo'lsa, backend serveri ishlayotganiga ishonch hosil qiling.
*   **ModuleNotFoundError:** Virtual muhit aktivligini va `pip install` muvaffaqiyatli o'tganini tekshiring.
*   **.env fayli:** Agar backend ishga tushmasa, `.env` fayli borligini tekshiring. Bo'lmasa, `.env.example` dan nusxa oling.

---

## 4. Talablar
*   Python 3.10 yoki undan yuqori
*   Node.js (LTS versiyasi tavsiya etiladi)
*   npm (Node.js bilan birga keladi)
