"""
AI Tools Registry — OpenAI va Anthropic uchun yagona manbaa.

Har bir tool quyidagi tuzilishga ega:
  name        : str   — noyob nom (snake_case)
  description : str   — AI uchun qachon/nima uchun ishlatish
  parameters  : dict  — JSON Schema (OpenAI format)
  handler     : callable(user, **kwargs) → dict

OpenAI uchun: tools[] -> {type: function, function: {name, description, parameters}}
Anthropic uchun: tools[] -> {name, description, input_schema}
"""

from datetime import date as _date

# ──────────────────────────────────────────────────────
# TOOL HANDLERLAR
# ──────────────────────────────────────────────────────

def _get_tasks(user, date=None, status=None, **_):
    """Foydalanuvchi vazifalarini qaytaradi."""
    from apps.tasks.models import Task
    qs = Task.objects.filter(user=user)
    if date:
        qs = qs.filter(date=date)
    if status == 'done':
        qs = qs.filter(done=True)
    elif status == 'pending':
        qs = qs.filter(done=False)
    tasks = list(qs.values('id', 'title', 'date', 'time', 'pri', 'cat', 'done'))
    return {'tasks': tasks, 'count': len(tasks)}


def _get_focus_summary(user, period='week', **_):
    """Focus sessiyalar xulosasini qaytaradi."""
    from apps.focus.models import FocusSession
    from datetime import timedelta
    today = _date.today()

    if period == 'today':
        sessions = FocusSession.objects.filter(user=user, date=today)
    elif period == 'week':
        week_start = today - timedelta(days=today.weekday())
        sessions = FocusSession.objects.filter(user=user, date__gte=week_start, date__lte=today)
    else:
        sessions = FocusSession.objects.filter(user=user)

    total_mins = sum(s.mins for s in sessions)
    streak_obj = getattr(user, 'streak', None)
    streak = streak_obj.count if streak_obj else 0

    return {
        'period': period,
        'total_minutes': total_mins,
        'total_hours': round(total_mins / 60, 1),
        'session_count': sessions.count(),
        'streak_days': streak,
    }


def _get_transaction_summary(user, period='month', **_):
    """Moliyaviy xulosani qaytaradi."""
    from apps.transactions.models import Transaction
    today = _date.today()
    qs = Transaction.objects.filter(user=user)

    if period == 'today':
        qs = qs.filter(iso_date=today)
    elif period == 'month':
        qs = qs.filter(iso_date__year=today.year, iso_date__month=today.month)

    income = sum(t.amt for t in qs if t.type == 'income')
    expense = sum(t.amt for t in qs if t.type == 'expense')
    return {
        'period': period,
        'income': income,
        'expense': expense,
        'net': income - expense,
        'currency': "so'm",
    }


def _complete_task(user, task_id, **_):
    """Vazifani bajarildi deb belgilaydi."""
    from apps.tasks.models import Task
    try:
        task = Task.objects.get(pk=task_id, user=user)
        task.done = True
        task.save(update_fields=['done'])
        return {'success': True, 'task_id': task_id, 'title': task.title}
    except Task.DoesNotExist:
        return {'success': False, 'error': 'Vazifa topilmadi'}


def _add_task(user, title, date=None, priority='gray', category='Boshqa', **_):
    """Yangi vazifa qo'shadi."""
    from apps.tasks.models import Task
    import re

    # Sanitizatsiya
    title = str(title).strip()[:500]
    if not title:
        return {'success': False, 'error': "Vazifa nomi bo'sh bo'lmasligi kerak"}

    # Priority tekshiruvi
    valid_priorities = ['danger', 'amber', 'gray']
    if priority not in valid_priorities:
        priority = 'gray'

    today = _date.today()
    # Sana format tekshiruvi
    task_date = today
    if date:
        if re.match(r'^\d{4}-\d{2}-\d{2}$', str(date)):
            try:
                from datetime import datetime
                task_date = datetime.strptime(str(date), '%Y-%m-%d').date()
            except ValueError:
                task_date = today
        else:
            task_date = today

    task = Task.objects.create(
        user=user,
        title=title,
        date=task_date,
        pri=priority,
        cat=str(category)[:100] if category else 'Boshqa',
    )
    return {'success': True, 'task_id': task.pk, 'title': task.title, 'date': str(task.date)}


# ──────────────────────────────────────────────────────
# REGISTRY — barcha toollar shu yerda
# ──────────────────────────────────────────────────────

TOOLS_REGISTRY = [
    {
        'name': 'get_tasks',
        'description': (
            "Foydalanuvchining vazifalarini olish. "
            "Bugungi, muayyan sana yoki barcha vazifalarni ko'rsatish mumkin. "
            "Foydalanuvchi 'mening vazifalarim', 'bugun nima bor', 'qanday ishlar qoldi' desa ishlatish."
        ),
        'parameters': {
            'type': 'object',
            'properties': {
                'date': {
                    'type': 'string',
                    'description': "Sana YYYY-MM-DD formatida (ixtiyoriy). Ko'rsatilmasa barcha vazifalar qaytariladi.",
                },
                'status': {
                    'type': 'string',
                    'enum': ['all', 'done', 'pending'],
                    'description': "Holat bo'yicha filtrlash: 'done' — bajarilgan, 'pending' — bajarilmagan.",
                },
            },
            'required': [],
        },
        'handler': _get_tasks,
    },
    {
        'name': 'get_focus_summary',
        'description': (
            "Focus sessiyalar statistikasini olish. "
            "Foydalanuvchi 'focus vaqtim', 'pomodoro', 'streak', 'qancha ishladim' desa ishlatish."
        ),
        'parameters': {
            'type': 'object',
            'properties': {
                'period': {
                    'type': 'string',
                    'enum': ['today', 'week', 'all'],
                    'description': "Davr: 'today' — bugun, 'week' — bu hafta, 'all' — barchasi.",
                },
            },
            'required': [],
        },
        'handler': _get_focus_summary,
    },
    {
        'name': 'get_transaction_summary',
        'description': (
            "Moliyaviy tranzaksiyalar xulosasini olish. "
            "Foydalanuvchi 'daromad', 'harajat', 'balans', 'pul' so'zlarini ishlatsa ishlatish."
        ),
        'parameters': {
            'type': 'object',
            'properties': {
                'period': {
                    'type': 'string',
                    'enum': ['today', 'month', 'all'],
                    'description': "Davr: 'today' — bugun, 'month' — bu oy, 'all' — barchasi.",
                },
            },
            'required': [],
        },
        'handler': _get_transaction_summary,
    },
    {
        'name': 'complete_task',
        'description': (
            "Vazifani bajarildi deb belgilash. "
            "Foydalanuvchi 'bajardim', 'tayyor', 'done qil' desa va task_id ma'lum bo'lsa ishlatish. "
            "Avval get_tasks bilan ID ni aniqlang."
        ),
        'parameters': {
            'type': 'object',
            'properties': {
                'task_id': {
                    'type': 'integer',
                    'description': 'Vazifaning ID raqami (get_tasks dan oling).',
                },
            },
            'required': ['task_id'],
        },
        'handler': _complete_task,
    },
    {
        'name': 'add_task',
        'description': (
            "Yangi vazifa qo'shish. "
            "Foydalanuvchi 'qo'sh', 'eslatma qo'y', 'vazifa yarat' desa ishlatish."
        ),
        'parameters': {
            'type': 'object',
            'properties': {
                'title': {
                    'type': 'string',
                    'description': 'Vazifa nomi.',
                },
                'date': {
                    'type': 'string',
                    'description': 'Sana YYYY-MM-DD formatida (ixtiyoriy, standart: bugun).',
                },
                'priority': {
                    'type': 'string',
                    'enum': ['danger', 'amber', 'gray'],
                    'description': "'danger' = muhim, 'amber' = o'rta, 'gray' = past.",
                },
                'category': {
                    'type': 'string',
                    'description': "Kategoriya nomi (standart: 'Boshqa').",
                },
            },
            'required': ['title'],
        },
        'handler': _add_task,
    },
]

# ──────────────────────────────────────────────────────
# PROVIDER-SPECIFIC FORMAT KONVERTORLAR
# ──────────────────────────────────────────────────────

def openai_tools_format():
    """OpenAI tools[] formatiga o'tkazish."""
    return [
        {
            'type': 'function',
            'function': {
                'name': t['name'],
                'description': t['description'],
                'parameters': t['parameters'],
            },
        }
        for t in TOOLS_REGISTRY
    ]


def anthropic_tools_format():
    """Anthropic tools[] formatiga o'tkazish."""
    return [
        {
            'name': t['name'],
            'description': t['description'],
            'input_schema': t['parameters'],
        }
        for t in TOOLS_REGISTRY
    ]


def get_handler(name):
    """Tool nomiga qarab handler funksiyasini topish."""
    for t in TOOLS_REGISTRY:
        if t['name'] == name:
            return t['handler']
    return None
