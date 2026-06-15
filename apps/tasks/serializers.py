from rest_framework import serializers
from .models import Task
from apps.categories.serializers import CategorySerializer

class TaskSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(
        write_only=True,
        required=False,
        allow_null=True
    )
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    date = serializers.DateField(
        format='%Y-%m-%d',
        input_formats=['%Y-%m-%d', 'iso-8601'],
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'time', 'pri',
            'category', 'category_id',
            'date', 'done', 'createdAt'
        ]
        read_only_fields = ['id', 'createdAt']

    def create(self, validated_data):
        category_id = validated_data.pop('category_id', None)
        if category_id:
            validated_data['category_id'] = category_id
        return super().create(validated_data)

    def update(self, instance, validated_data):
        category_id = validated_data.pop('category_id', None)
        if category_id is not None:
            instance.category_id = category_id
        return super().update(instance, validated_data)
