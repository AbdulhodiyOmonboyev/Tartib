from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


def get_tokens_for_user(user):
    """Foydalanuvchi uchun access va refresh tokenlarni yaratish."""
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


class UserSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(source='first_name')
    lastName = serializers.CharField(source='last_name')
    telegramId = serializers.IntegerField(source='telegram_id', required=False, allow_null=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'firstName', 'lastName', 'telegramId', 'createdAt']


class RegisterSerializer(serializers.Serializer):
    firstName = serializers.CharField(max_length=100)
    lastName = serializers.CharField(max_length=100, required=False, default='')
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError('Bu email allaqachon ro\'yxatdan o\'tgan')
        return value.lower()

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['firstName'],
            last_name=validated_data.get('lastName', ''),
        )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['email'].lower(), password=data['password'])
        if not user:
            raise serializers.ValidationError('Email yoki parol noto\'g\'ri')
        if not user.is_active:
            raise serializers.ValidationError('Hisob bloklangan')
        data['user'] = user
        return data


class SettingsUpdateSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(source='first_name', required=False)
    lastName = serializers.CharField(source='last_name', required=False)
    telegramId = serializers.IntegerField(source='telegram_id', required=False, allow_null=True)
    currentPassword = serializers.CharField(write_only=True, required=False)
    newPassword = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = User
        fields = ['firstName', 'lastName', 'email', 'telegramId', 'currentPassword', 'newPassword']

    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.filter(email=value.lower()).exclude(pk=user.pk).exists():
            raise serializers.ValidationError('Bu email allaqachon ishlatilmoqda')
        return value.lower()

    def validate(self, data):
        current = data.pop('currentPassword', None)
        new_pw = data.pop('newPassword', None)
        if new_pw:
            if not current:
                raise serializers.ValidationError(
                    {'currentPassword': 'Yangi parol uchun joriy parolni kiriting'}
                )
            user = self.context['request'].user
            if not user.check_password(current):
                raise serializers.ValidationError(
                    {'currentPassword': 'Joriy parol noto\'g\'ri'}
                )
            data['_new_password'] = new_pw
        return data

    def update(self, instance, validated_data):
        new_pw = validated_data.pop('_new_password', None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        if new_pw:
            instance.set_password(new_pw)
        instance.save()
        return instance
