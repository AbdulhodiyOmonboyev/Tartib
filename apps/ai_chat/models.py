from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from cryptography.fernet import Fernet
from django.conf import settings
import base64
import hashlib


def get_cipher():
    """Shifrlash kalitini olish."""
    key = settings.CRYPTOGRAPHY_KEY
    # 32 baytli kalit kerak (base64 formatida)
    if isinstance(key, str):
        key = key.encode()
    # SHA-256 qo'llash orqali 32 baytli kalit yaratish
    key_hash = hashlib.sha256(key).digest()
    key_b64 = base64.urlsafe_b64encode(key_hash)
    return Fernet(key_b64)


class EncryptedField(models.CharField):
    """Custom CharField shifrlash bilan."""
    def get_prep_value(self, value):
        if value is None:
            return value
        cipher = get_cipher()
        if isinstance(value, str):
            value = value.encode()
        encrypted = cipher.encrypt(value)
        return encrypted.decode()
    
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        try:
            cipher = get_cipher()
            decrypted = cipher.decrypt(value.encode())
            return decrypted.decode()
        except Exception:
            return value


class AISettings(models.Model):
    PROVIDER_CHOICES = [
        ('openai', 'OpenAI (ChatGPT)'),
        ('anthropic', 'Anthropic (Claude)'),
        ('gemini', 'Google Gemini (tekin)'),
        ('ollama', 'Ollama (mahalliy, bepul)'),
        ('offline', 'AI siz (mahalliy algoritm)'),
    ]

    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
        default='openai',
        verbose_name='Provider'
    )
    api_key = EncryptedField(
        max_length=500,
        verbose_name='API kalit',
        help_text='OpenAI yoki Anthropic API kaliti (shifrlangan holda saqlanadi)'
    )
    model_name = models.CharField(
        max_length=100,
        default='gpt-4o-mini',
        verbose_name='Model nomi',
        help_text='Masalan: gpt-4o-mini, gpt-4o, claude-3-haiku-20240307'
    )
    system_prompt = models.TextField(
        verbose_name='System prompt',
        default="""Sen "Tartib" deb nomlangan O'zbek tilidagi shaxsiy samaradorlik ilovasi uchun AI maslahatchi yordamchisisan.
Foydalanuvchilar sening bilan o'z vazifalari, focus vaqtlari, daromadlari va ish rejalari haqida suhbatlashadilar.

Qoidalar:
1. Har doim O'zbek tilida javob ber
2. Qisqa, aniq va amaliy maslahatlar ber
3. Foydalanuvchi ma'lumotlariga (vazifalar, focus, daromad) asoslanib javob ber
4. Do'stona va rag'batlantiruvchi tonda gapir
5. HTML teglari ishlatmaslik, oddiy matn yoz
6. Javob 3-5 jumladan uzun bo'lmasin""",
        help_text='AI ning xulq-atvori va vazifasini belgilovchi prompt'
    )
    max_tokens = models.PositiveIntegerField(
        default=500,
        verbose_name='Maksimal tokenlar',
        validators=[MinValueValidator(50), MaxValueValidator(4096)],
        help_text='50 dan 4096 gacha'
    )
    temperature = models.FloatField(
        default=0.7,
        verbose_name='Harorat (0.0-2.0)',
        validators=[MinValueValidator(0.0), MaxValueValidator(2.0)],
        help_text='0 = aniq, 1 = kreativ, 2 = tasodifiy'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Faol',
        help_text='Bu sozlamani ishlatish'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'AI Sozlamalar'
        verbose_name_plural = 'AI Sozlamalar'

    def __str__(self):
        return f'{self.get_provider_display()} — {self.model_name} ({"Faol" if self.is_active else "Nofaol"})'


class ChatHistory(models.Model):
    """Ixtiyoriy — chat tarixini saqlash uchun."""
    user = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='chat_history',
        verbose_name='Foydalanuvchi'
    )
    role = models.CharField(max_length=10, choices=[('user', 'Foydalanuvchi'), ('assistant', 'AI')])
    content = models.TextField(verbose_name='Xabar')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Chat tarixi'
        verbose_name_plural = 'Chat tarixi'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.user.email} — {self.role}: {self.content[:50]}'
