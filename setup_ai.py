import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tartib.settings')
django.setup()

from apps.ai_chat.models import AISettings
from decouple import config

# Create Gemini config
AISettings.objects.get_or_create(
    provider='gemini',
    defaults={
        'api_key': config('GEMINI_API_KEY', default='Sizning-Gemini-API-Kalitingiz'),
        'model_name': 'gemini-1.5-flash',
        'is_active': False
    }
)

# Create Ollama config
AISettings.objects.get_or_create(
    provider='ollama',
    defaults={
        'api_key': 'not-needed',
        'model_name': 'llama3',
        'is_active': False
    }
)

# Set offline as active by default if none is active
if not AISettings.objects.filter(is_active=True).exists():
    offline_setting, created = AISettings.objects.get_or_create(
        provider='offline',
        defaults={
            'api_key': 'not-needed',
            'model_name': 'offline',
            'is_active': True
        }
    )
    if not created and not offline_setting.is_active:
        offline_setting.is_active = True
        offline_setting.save()

print("AI sozlamalari yaratildi.")
