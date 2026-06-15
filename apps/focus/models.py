from django.db import models
from django.conf import settings


class FocusSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='focus_sessions',
        verbose_name='Foydalanuvchi'
    )
    date = models.DateField(verbose_name='Sana')
    mins = models.PositiveIntegerField(verbose_name='Daqiqalar')
    hour = models.PositiveSmallIntegerField(verbose_name='Soat (0-23)')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Focus seansi'
        verbose_name_plural = 'Focus seanslar'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} — {self.date} ({self.mins} daqiqa)'


class UserStreak(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='streak',
        verbose_name='Foydalanuvchi'
    )
    count = models.PositiveIntegerField(default=0, verbose_name='Streak soni')
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Streak'
        verbose_name_plural = 'Streaklar'

    def __str__(self):
        return f'{self.user.email} — {self.count} kun'
