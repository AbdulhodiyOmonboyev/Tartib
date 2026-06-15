@echo off
setlocal enabledelayedexpansion

:: 1. Loyiha papkasini aniqlash (Bo'sh joylar bilan ishlash uchun)
set "BASE_DIR=%~dp0"
if "%BASE_DIR:~-1%"=="\" set "BASE_DIR=%BASE_DIR:~0,-1%"
cd /d "%BASE_DIR%"

echo ========================================================
echo   TARTIB Productivity Platform - Avtomatik Setup
echo ========================================================
echo Project Root: "%BASE_DIR%"
echo.

:: 2. .env fayllarni tekshirish
echo [1/6] Konfiguratsiya fayllarini tekshirish...
if not exist ".env" (
    if exist ".env.example" (
        echo Backend .env yaratilmoqda...
        copy ".env.example" ".env" >nul
    )
)
if exist "template" (
    if not exist "template\.env" (
        if exist "template\.env.example" (
            echo Frontend .env yaratilmoqda...
            copy "template\.env.example" "template\.env" >nul
        )
    )
)

:: 3. Pythonni tekshirish
echo [2/6] Python muhitini tekshirish...
python --version >nul 2>&1
if errorlevel 1 (
    echo XATO: Python o'rnatilmagan yoki PATH ga qo'shilmagan!
    echo Iltimos, Pythonni o'rnating: https://www.python.org/
    pause
    exit /b 1
)

:: 4. Virtual muhitni (venv) tekshirish
if not exist "venv" (
    echo [3/6] Virtual muhit yaratilmoqda (venv)...
    python -m venv venv
    if errorlevel 1 (
        echo XATO: Virtual muhitni yaratib bo'lmadi!
        pause
        exit /b 1
    )
) else (
    echo [3/6] Virtual muhit mavjud.
)

:: Venv yo'llari (Qo'shtirnoqsiz set qilinadi, ishlatganda qo'shtirnoq qo'yiladi)
set "V_PYTHON=%BASE_DIR%\venv\Scripts\python.exe"
set "V_PIP=%BASE_DIR%\venv\Scripts\pip.exe"

:: 5. Backend kutubxonalarini o'rnatish
echo [4/6] Backend kutubxonalarini tekshirish...
"%V_PIP%" show django >nul 2>&1
if errorlevel 1 (
    echo Kutubxonalar o'rnatilmoqda (bu bir oz vaqt olishi mumkin)...
    "%V_PIP%" install -r requirements.txt
    if errorlevel 1 (
        echo XATO: Kutubxonalarni o'rnatishda xatolik yuz berdi!
        pause
        exit /b 1
    )
) else (
    echo Backend kutubxonalari tayyor.
)

:: 6. Migratsiya
echo [5/6] Ma'lumotlar bazasini yangilash...
"%V_PYTHON%" manage.py migrate --noinput
if errorlevel 1 (
    echo XATO: Migratsiya vaqtida xatolik yuz berdi!
    pause
    exit /b 1
)

:: 7. Frontend (npm)
echo [6/6] Frontend muhitini tekshirish...
set "FE_DIR=%BASE_DIR%\template"
if exist "%FE_DIR%\package.json" (
    if not exist "%FE_DIR%\node_modules" (
        echo Frontend kutubxonalari o'rnatilmoqda (npm install)...
        cd /d "%FE_DIR%"
        call npm install
        cd /d "%BASE_DIR%"
    ) else (
        echo Frontend kutubxonalari tayyor.
    )
)

echo.
echo ========================================================
echo   LOYIHA ISHGA TUSHISHGA TAYYOR!
echo ========================================================
echo.
echo  Backend:  http://localhost:8000
echo  Frontend: http://localhost:5173
echo.
echo  Serverlar alohida oynalarda ishga tushadi. Ularni yopmang.
echo.

:: 8. Ishga tushirish (START /D ishlatiladi - bu eng xavfsiz yo'l)

:: Backend
start "TARTIB BACKEND" /D "%BASE_DIR%" cmd /k venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000

:: Frontend
if exist "%FE_DIR%\package.json" (
    start "TARTIB FRONTEND" /D "%FE_DIR%" cmd /k npm run dev
)

echo.
echo Barchasi muvaffaqiyatli ishga tushdi! 
echo 10 soniyadan so'ng bu oyna yopiladi.
timeout /t 10
exit
