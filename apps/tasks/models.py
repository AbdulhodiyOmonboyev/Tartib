from django.db import models
from django.conf import settings


class Task(models.Model):
    PRI_CHOICES = [
        ('danger', 'Muhim'),
        ('amber', "O'rta"),
        ('gray', 'Past'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Foydalanuvchi'
    )
    title = models.CharField(max_length=500, verbose_name='Nomi')
    time = models.CharField(max_length=20, blank=True, default='')
    pri = models.CharField(max_length=10, choices=PRI_CHOICES, default='gray')
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name='Kategoriya'
    )
    date = models.DateField(null=True, blank=True)
    done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Vazifa'
        verbose_name_plural = 'Vazifalar'
        ordering = ['date', 'time', '-created_at']

    def __str__(self):
        return f'{self.title} ({self.user.email})'
