from django.contrib import admin
from .models import AISettings, ChatHistory


@admin.register(AISettings)
class AISettingsAdmin(admin.ModelAdmin):
    list_display = ['provider', 'model_name', 'max_tokens', 'temperature', 'is_active', 'created_at']
    list_filter = ['provider', 'is_active']
    list_editable = ['is_active']

    fieldsets = (
        ('Asosiy sozlamalar', {
            'fields': ('provider', 'api_key', 'model_name', 'is_active')
        }),
        ('Model parametrlari', {
            'fields': ('max_tokens', 'temperature')
        }),
        ('System prompt', {
            'fields': ('system_prompt',),
            'classes': ('wide',),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['api_key'].widget.attrs['style'] = 'width: 100%;'
        form.base_fields['system_prompt'].widget.attrs['rows'] = 15
        return form


@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'content_preview', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__email', 'content']
    ordering = ['-created_at']
    raw_id_fields = ['user']

    @admin.display(description='Xabar')
    def content_preview(self, obj):
        return obj.content[:80] + '...' if len(obj.content) > 80 else obj.content
