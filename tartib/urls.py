from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from .views import HomeView, api_info
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# Admin panel nomi
admin.site.site_header = 'Tartib Admin'
admin.site.site_title = 'Tartib'
admin.site.index_title = 'Boshqaruv paneli'

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({'status': 'ok', 'message': 'Tartib API ishlayapti'})

@api_view(['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@permission_classes([AllowAny])
def catch_all_api(request, path=None):
    """Noto'g'ri API yo'llarni tutadigan fallback"""
    return Response({
        'error': 'Path not found',
        'requested_path': request.path,
        'available_endpoints': {
            'admin': '/admin',
            'auth': '/api/auth/register, /api/auth/login, /api/auth/me',
            'tasks': '/api/tasks/',
            'transactions': '/api/transactions/',
            'focus': '/api/focus/sessions, /api/focus/streak',
            'categories': '/api/categories/',
            'ai': '/api/ai/chat/',
        }
    }, status=404)

urlpatterns = [
    path('', health_check),
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.authentication.urls')),
    path('api/tasks/', include('apps.tasks.urls')),
    path('api/transactions/', include('apps.transactions.urls')),
    path('api/focus/', include('apps.focus.urls')),
    path('api/categories/', include('apps.categories.urls')),
    path('api/settings/', include('apps.authentication.settings_urls')),
    path('api/ai/', include('apps.ai_chat.urls')),
    path('api/<path:path>', catch_all_api),  # Noto'g'ri API yo'lar uchun
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
