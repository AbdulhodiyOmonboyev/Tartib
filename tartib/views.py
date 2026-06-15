from django.views.generic import TemplateView
from django.http import JsonResponse

class HomeView(TemplateView):
    template_name = 'index.html'

def api_info(request):
    """API endpoint ma'lumotlari"""
    return JsonResponse({
        'name': 'Tartib API',
        'version': '1.0.0',
        'description': 'Personal productivity API',
        'endpoints': {
            'auth': '/api/auth/register, /api/auth/login, /api/auth/me',
            'tasks': '/api/tasks',
            'transactions': '/api/transactions',
            'focus': '/api/focus/sessions, /api/focus/streak',
            'categories': '/api/categories',
            'ai': '/api/ai/chat',
        },
        'admin': '/admin/',
        'docs': '/api/docs/'
    })
