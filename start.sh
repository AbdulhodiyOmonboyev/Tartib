#!/bin/bash
# Стартовый скрипт для TARTIB Django Backend (Linux/Mac)

echo "========================================"
echo "   TARTIB Backend Startup"
echo "========================================"

# Активировать venv
echo ""
echo "[1/4] Activating virtual environment..."
source venv/bin/activate

# Установить зависимости если нужно
echo "[2/4] Checking dependencies..."
if ! pip show django &> /dev/null; then
    echo "Installing requirements..."
    pip install -r requirements.txt
fi

# Запустить миграции если нужно
if [ ! -f "db.sqlite3" ]; then
    echo "[3/4] Running migrations..."
    python manage.py migrate
    
    echo ""
    echo "[4/4] Creating superuser..."
    python manage.py createsuperuser
fi

echo ""
echo "========================================"
echo "   Starting Django development server"
echo "========================================"
echo ""
echo "Backend will be available at:"
echo "   - API: http://localhost:8000/api"
echo "   - Admin: http://localhost:8000/admin"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

# Запустить сервер
python manage.py runserver 0.0.0.0:8000
