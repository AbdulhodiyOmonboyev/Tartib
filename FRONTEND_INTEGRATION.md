# Frontend API Integration Guide

Этот файл содержит инструкции по интеграции React frontend приложения с Django backend API.

## 1. Frontend .env конфигурация

Создайте файл `template/.env` (или обновите `template/.env.example`):

```env
VITE_API_URL=http://localhost:8000/api
```

Для production:
```env
VITE_API_URL=https://your-domain.com/api
```

## 2. API Service (src/services/api.js)

Убедитесь что в `src/services/api.js` есть базовая конфигурация:

```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const apiFetch = async (endpoint, options = {}) => {
  const token = localStorage.getItem('t_token');
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'API Error');
  }
  
  if (response.status === 204) {
    return null;
  }
  
  return response.json();
};

export const authApi = {
  register: (firstName, lastName, email, password) =>
    apiFetch('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ firstName, lastName, email, password }),
    }),
    
  login: (email, password) =>
    apiFetch('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
    
  me: () => apiFetch('/auth/me'),
  
  logout: () =>
    apiFetch('/auth/logout', { method: 'POST' }),
};

export const taskApi = {
  list: () => apiFetch('/tasks'),
  create: (data) =>
    apiFetch('/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  update: (id, data) =>
    apiFetch(`/tasks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  delete: (id) =>
    apiFetch(`/tasks/${id}`, { method: 'DELETE' }),
};

export const transactionApi = {
  list: () => apiFetch('/transactions'),
  create: (data) =>
    apiFetch('/transactions', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  delete: (id) =>
    apiFetch(`/transactions/${id}`, { method: 'DELETE' }),
};

export const focusApi = {
  listSessions: () => apiFetch('/focus/sessions'),
  createSession: (data) =>
    apiFetch('/focus/sessions', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  getStreak: () => apiFetch('/focus/streak'),
  updateStreak: (count) =>
    apiFetch('/focus/streak', {
      method: 'PUT',
      body: JSON.stringify({ count }),
    }),
};

export const categoryApi = {
  list: () => apiFetch('/categories'),
  create: (name) =>
    apiFetch('/categories', {
      method: 'POST',
      body: JSON.stringify({ name }),
    }),
  delete: (name) =>
    apiFetch(`/categories/${name}`, { method: 'DELETE' }),
};

export const aiApi = {
  chat: (message, context) =>
    apiFetch('/ai/chat', {
      method: 'POST',
      body: JSON.stringify({ message, context }),
    }),
};

export const settingsApi = {
  get: () => apiFetch('/settings'),
  update: (data) =>
    apiFetch('/settings', {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
};
```

## 3. Token Management

Frontend должен:

1. **При успешной регистрации/логине:**
   ```javascript
   const { token, user } = response;
   localStorage.setItem('t_token', token);
   localStorage.setItem('user', JSON.stringify(user));
   ```

2. **При загрузке приложения:**
   ```javascript
   const token = localStorage.getItem('t_token');
   if (token) {
     // Проверить валидность токена
     try {
       const user = await authApi.me();
       // Токен валиден
     } catch (e) {
       localStorage.removeItem('t_token');
       // Редирект на логин
     }
   }
   ```

3. **При выходе:**
   ```javascript
   localStorage.removeItem('t_token');
   localStorage.removeItem('user');
   // Редирект на логин
   ```

## 4. Error Handling

Все ошибки имеют формат:
```json
{
  "message": "Описание ошибки"
}
```

Пример обработки:
```javascript
try {
  await taskApi.create(task);
} catch (error) {
  showToast('error', error.message);
}
```

## 5. CORS Configuration

Если видите CORS ошибку в консоли браузера:

1. Проверьте что backend запущен на `http://localhost:8000`
2. Проверьте `.env` файл backend: `CORS_ALLOWED_ORIGINS=http://localhost:5173`
3. Перезагрузите backend сервер

## 6. Development vs Production

### Development (localhost)
```env
VITE_API_URL=http://localhost:8000/api
```
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

### Production
```env
VITE_API_URL=https://api.yourdomain.com/api
```
- Backend: Развернут на вашем сервере с HTTPS
- Frontend: Может быть на том же домене

## 7. Testing Endpoints с curl

```bash
# Регистрация
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "Test",
    "lastName": "User",
    "email": "test@example.com",
    "password": "testpass123"
  }'

# Логин
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'

# Получить профиль (замените TOKEN на реальный токен)
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer TOKEN"

# Создать задачу
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Task",
    "time": "10:00-11:00",
    "pri": "danger",
    "cat": "Work",
    "date": "2025-05-15"
  }'
```

## 8. Troubleshooting

### Ошибка: "Network Error"
- Проверьте что backend сервер запущен: `python manage.py runserver`
- Проверьте URL в `VITE_API_URL`

### Ошибка: "401 Unauthorized"
- Токен не отправлен или истек
- Проверьте `localStorage.t_token`

### Ошибка: "403 Forbidden"
- У пользователя нет прав
- Убедитесь что вы авторизованы

### Ошибка: "404 Not Found"
- Неправильный URL endpoint
- Проверьте путь запроса

## Примечания

- Все даты отправляйте в формате `YYYY-MM-DD`
- Все суммы в копейках/тийинах (целые числа)
- Используйте camelCase для всех полей в frontend
- Backend автоматически преобразует camelCase → snake_case
