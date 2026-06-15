from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'pri', 'category', 'date', 'done', 'created_at']
    list_filter = ['pri', 'category', 'done', 'created_at']
    search_fields = ['title', 'user__email']
    list_editable = ['done']
    ordering = ['-created_at']
    raw_id_fields = ['user', 'category']
