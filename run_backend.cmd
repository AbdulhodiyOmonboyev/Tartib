@echo off
REM Backend Django Serverini ishga tushirish
REM Foydalanish: Double-click qiling yoki cmd da run_backend.cmd

setlocal enabledelayedexpansion
set "BASE_DIR=%~dp0"
if "%BASE_DIR:~-1%"=="\" set "BASE_DIR=%BASE_DIR:~0,-1%"

cd /d "%BASE_DIR%"

echo ========================================
echo   TARTIB Backend Server
echo ========================================
echo.

REM Venv faol qilish
call venv\Scripts\activate.bat

REM Django serverini ishga tushirish
echo Backend http://localhost:8000 da ishga tushmoqda...
echo.
echo Serverni to'xtattish uchun: CTRL + C
echo.

python manage.py runserver 0.0.0.0:8000

pause
