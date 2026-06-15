from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Transaction(models.Model):
    TYPE_CHOICES = [
        ('income', 'Daromad'),
        ('expense', 'Harajat'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name='Foydalanuvchi'
    )
    name = models.CharField(max_length=300, verbose_name='Nomi')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name='Turi')
    amt = models.BigIntegerField(
        verbose_name="Miqdor (so'm)",
        validators=[MinValueValidator(1)]
    )
    cat = models.CharField(max_length=100, default='Boshqa', verbose_name='Kategoriya')
    date = models.CharField(max_length=20, blank=True, default='', verbose_name='Sana (15 may)')
    iso_date = models.DateField(null=True, blank=True, verbose_name='ISO sana')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Tranzaksiya'
        verbose_name_plural = 'Tranzaksiyalar'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.amt:,} so\'m ({self.type})'
