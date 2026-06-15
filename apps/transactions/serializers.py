from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    isoDate = serializers.DateField(
        source='iso_date',
        format='%Y-%m-%d',
        input_formats=['%Y-%m-%d', 'iso-8601'],
        required=False,
        allow_null=True,
    )
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'name', 'type', 'amt', 'cat', 'date', 'isoDate', 'createdAt']
        read_only_fields = ['id', 'createdAt']
