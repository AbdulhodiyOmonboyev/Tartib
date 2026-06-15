from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    get_tokens_for_user, SettingsUpdateSerializer
)


@method_decorator(
    ratelimit(key='ip', rate='5/m', method='POST', block=True),
    name='dispatch'
)
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if getattr(request, 'limited', False):
            return Response(
                {'message': "Juda ko'p urinish. 1 daqiqadan so'ng qayta urining."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response({
                'token': token,
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response({'message': list(serializer.errors.values())[0][0]},
                        status=status.HTTP_400_BAD_REQUEST)


@method_decorator(
    ratelimit(key='ip', rate='10/m', method='POST', block=True),
    name='dispatch'
)
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if getattr(request, 'limited', False):
            return Response(
                {'message': "Juda ko'p urinish. 1 daqiqadan so'ng qayta urining."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token = get_tokens_for_user(user)
            return Response({
                'token': token,
                'user': UserSerializer(user).data
            })
        return Response({'message': list(serializer.errors.values())[0][0]},
                        status=status.HTTP_401_UNAUTHORIZED)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if refresh_token:
            try:
                from rest_framework_simplejwt.tokens import RefreshToken
                from rest_framework_simplejwt.exceptions import TokenError
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass  # Token allaqachon noto'g'ri yoki blacklist yo'q
        return Response({'message': 'Muvaffaqiyatli chiqildi'})


# Settings views — /api/settings
class SettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        serializer = SettingsUpdateSerializer(
            request.user, data=request.data, partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(request.user).data)
        return Response({'message': list(serializer.errors.values())[0][0]},
                        status=status.HTTP_400_BAD_REQUEST)
