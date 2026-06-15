from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'type', 'amt_display', 'cat', 'iso_date', 'created_at']
    list_filter = ['type', 'cat', 'created_at']
    search_fields = ['name', 'user__email']
    ordering = ['-created_at']
    raw_id_fields = ['user']

    @admin.display(description="Miqdor (so'm)")
    def amt_display(self, obj):
        return f'{obj.amt:,}'
