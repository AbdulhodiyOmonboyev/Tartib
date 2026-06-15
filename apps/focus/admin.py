from django.contrib import admin
from .models import FocusSession, UserStreak


@admin.register(FocusSession)
class FocusSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'mins', 'hour', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['user__email']
    ordering = ['-created_at']
    raw_id_fields = ['user']


@admin.register(UserStreak)
class UserStreakAdmin(admin.ModelAdmin):
    list_display = ['user', 'count', 'last_updated']
    search_fields = ['user__email']
    ordering = ['-count']
    raw_id_fields = ['user']
