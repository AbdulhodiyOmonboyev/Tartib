from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Category
from .serializers import CategorySerializer


class CategoryListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Default kategoriyalar borligiga ishonch hosil qilish
        defaults = ["Ish", "O'rganish", "Shaxsiy", "Sog'liq", "Boshqa"]
        for name in defaults:
            Category.objects.get_or_create(user=request.user, name=name)
            
        categories = Category.objects.filter(user=request.user)
        return Response(CategorySerializer(categories, many=True).data)

    def post(self, request):
        name = request.data.get('name', '').strip()
        if not name:
            return Response({'message': 'Kategoriya nomi kiritilmagan'},
                            status=status.HTTP_400_BAD_REQUEST)
        cat, created = Category.objects.get_or_create(user=request.user, name=name)
        if not created:
            return Response({'message': 'Bu kategoriya allaqachon mavjud'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({'name': cat.name}, status=status.HTTP_201_CREATED)


class CategoryDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, name):
        try:
            cat = Category.objects.get(user=request.user, name=name)
            cat.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Category.DoesNotExist:
            return Response({'message': 'Topilmadi'}, status=status.HTTP_404_NOT_FOUND)
