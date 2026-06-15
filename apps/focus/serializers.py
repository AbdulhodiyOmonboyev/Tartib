from rest_framework import serializers
from .models import FocusSession, UserStreak


class FocusSessionSerializer(serializers.ModelSerializer):
    date = serializers.DateField(
        format='%Y-%m-%d',
        input_formats=['%Y-%m-%d', 'iso-8601'],
    )

    class Meta:
        model = FocusSession
        fields = ['id', 'date', 'mins', 'hour']
        read_only_fields = ['id']


class StreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStreak
        fields = ['count']
