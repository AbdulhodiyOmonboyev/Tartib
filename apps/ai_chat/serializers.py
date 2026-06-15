from rest_framework import serializers
from .models import AISettings, ChatHistory


class AISettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AISettings
        fields = ['provider', 'model_name', 'max_tokens', 'temperature', 'is_active']


class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory
        fields = ['role', 'content', 'created_at']
