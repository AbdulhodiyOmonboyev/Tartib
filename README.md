# TARTIB Backend — Django REST API

Полный Django backend для мобильного приложения TARTIB (управление задачами, финансами, focus-сеансами и AI-консультантом).

## Быстрый старт

### 1. Активировать виртуальное окружение

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Установить зависимости (если еще не установлены)

```bash
pip install -r requirements.txt
```

### 3. Создать .env файл

Скопируйте `.env.example` в `.env` и обновите значения:

```bash
cp .env.example .env
```

Обязательно установите:
- `SECRET_KEY` — уникальный ключ Django (можно сгенерировать: `django-admin shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- `DEBUG=False` для production
- `CORS_ALLOWED_ORIGINS` — адреса frontend приложения

### 4. Запустить миграции (только при первом запуске)

```bash
python manage.py makemigrations
python manage.py migrate
```

⚠️ **ВАЖНО**: После обновления миграций API ключи будут зашифрованы. Если у вас были сохраненные ключи, необходимо повторно ввести их в админ-панели (Settings > AI Sozlamalar). Старые незашифрованные значения будут заменены.

### 5. Создать суперпользователя (только при первом запуске)

```bash
python manage.py createsuperuser
```

Введите:
- Email: `admin@tartib.uz`
- First name: `Admin`
- Password: (введите надежный пароль)

### 6. Запустить сервер разработки

```bash
python manage.py runserver
```

Сервер будет доступен на `http://localhost:8000`
Admin-панель: `http://localhost:8000/admin`

---

## Архитектура приложений

```
apps/
├── authentication/   - Custom User, регистрация, логин, профиль
├── tasks/            - CRUD для задач
├── transactions/     - Доход/Расход (финансы)
├── focus/            - Focus-сеансы и streak-счетчик
├── categories/       - Пользовательские категории
└── ai_chat/          - AI-консультант (OpenAI/Claude)
```

---

## API Endpoints

### Authentication (`/api/auth`)

| Метод | URL | Описание |
|-------|-----|---------|
| POST | `/register` | Регистрация нового пользователя |
| POST | `/login` | Вход и получение JWT токена |
| GET | `/me` | Получить данные текущего пользователя |
| POST | `/logout` | Выход |

### Tasks (`/api/tasks`)

| Метод | URL | Описание |
|-------|-----|---------|
| GET | `/` | Список задач текущего пользователя |
| POST | `/` | Создать новую задачу |
| PUT | `/<id>` | Обновить задачу |
| DELETE | `/<id>` | Удалить задачу |

### Transactions (`/api/transactions`)

| Метод | URL | Описание |
|-------|-----|---------|
| GET | `/` | Список финансовых операций |
| POST | `/` | Создать новую операцию |
| DELETE | `/<id>` | Удалить операцию |

### Focus (`/api/focus`)

| Метод | URL | Описание |
|-------|-----|---------|
| GET | `/sessions` | Список focus-сеансов |
| POST | `/sessions` | Создать новый сеанс |
| GET | `/streak` | Получить текущий streak |
| PUT | `/streak` | Обновить streak |

### Categories (`/api/categories`)

| Метод | URL | Описание |
|-------|-----|---------|
| GET | `/` | Список категорий пользователя |
| POST | `/` | Создать новую категорию |
| DELETE | `/<name>` | Удалить категорию |

### AI Chat (`/api/ai`)

| Метод | URL | Описание |
|-------|-----|---------|
| POST | `/chat` | Отправить сообщение AI-консультанту |

### Settings (`/api/settings`)

| Метод | URL | Описание |
|-------|-----|---------|
| GET | `/` | Получить профиль |
| PUT | `/` | Обновить профиль |

---

## AI Настройка

### 1. Откройте Admin-панель

Перейдите на `http://localhost:8000/admin` с учетными данными суперпользователя.

### 2. Добавьте AI Settings

- Перейдите на **AI Sozlamalar** → **Add AI Settings**
- Выберите **Provider** (OpenAI или Anthropic)
- Введите **API key** (получите на OpenAI.com или Anthropic.com)
- Выберите **Model name**:
  - OpenAI: `gpt-4o-mini` (рекомендуется), `gpt-4o`, `gpt-3.5-turbo`
  - Anthropic: `claude-3-haiku-20240307`, `claude-3-sonnet-20240229`
- Установите **is_active = True**

### 3. Проверьте в приложении

Откройте AI Chat в мобильном приложении и отправьте сообщение.

---

## Структура данных

### Формат токена

Frontend получает JWT токен в ответе на `/api/auth/login`:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "firstName": "Имя",
    "lastName": "Фамилия",
    "createdAt": "2025-05-15T10:00:00Z"
  }
}
```

Frontend сохраняет токен в `localStorage.t_token` и отправляет в каждом запросе:

```
Authorization: Bearer {token}
```

### Формат ошибок

Все ошибки возвращаются в формате:

```json
{
  "message": "Описание ошибки"
}
```

---

## Командные команды

```bash
# Создать новые миграции
python manage.py makemigrations

# Применить миграции
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser

# Открыть интерпретатор Django
python manage.py shell

# Работать с DB directly
python manage.py dbshell

# Собрать статические файлы
python manage.py collectstatic

# Запустить тесты (если есть)
python manage.py test

# Очистить временные файлы
python manage.py flush
```

---

## Production развертывание

Для production используйте:

1. **Gunicorn** — WSGI сервер
2. **PostgreSQL** — базу данных (вместо SQLite)
3. **Nginx** — обратный прокси
4. **SSL/TLS** — шифрованное соединение
5. **Environment variables** — все чувствительные данные в .env

Пример запуска с Gunicorn:

```bash
pip install gunicorn
gunicorn tartib.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

---

## Решение проблем

### "ModuleNotFoundError: No module named 'django'"

Активируйте виртуальное окружение:
```bash
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### CORS ошибки в браузере

Убедитесь, что `CORS_ALLOWED_ORIGINS` в `.env` содержит адрес frontend:

```
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### "Couldn't import Django"

Переустановите зависимости:
```bash
pip install -r requirements.txt
```

---

## Контакт

Для вопросов и проблем обратитесь к документации в `template/BACKEND_GUIDE.md`.
