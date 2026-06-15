from datetime import date, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import FocusSession, UserStreak
from .serializers import FocusSessionSerializer, StreakSerializer


class FocusSessionListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = FocusSession.objects.filter(user=request.user)
        return Response(FocusSessionSerializer(sessions, many=True).data)

    def post(self, request):
        serializer = FocusSessionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'message': list(serializer.errors.values())[0][0]},
                        status=status.HTTP_400_BAD_REQUEST)


class StreakView(APIView):
    permission_classes = [IsAuthenticated]

    def _calculate_streak(self, user):
        """FocusSession'lar asosida ketma-ket kunlar sonini hisoblash."""
        today = date.today()
        streak = 0
        current_date = today

        session_dates = set(
            FocusSession.objects.filter(user=user)
            .values_list('date', flat=True)
        )

        # Bugundan orqaga qarab ketma-ket kunlarni sanash
        while current_date in session_dates:
            streak += 1
            current_date -= timedelta(days=1)

        return streak

    def get(self, request):
        streak_obj, _ = UserStreak.objects.get_or_create(user=request.user)
        # Har safar real hisoblash
        real_streak = self._calculate_streak(request.user)
        if streak_obj.count != real_streak:
            streak_obj.count = real_streak
            streak_obj.save()
        return Response({'count': real_streak})

    def post(self, request):
        """Focus seansi tugaganda chaqiriladi — streak qayta hisoblanadi."""
        streak_obj, _ = UserStreak.objects.get_or_create(user=request.user)
        new_count = self._calculate_streak(request.user)
        streak_obj.count = new_count
        streak_obj.save()
        return Response({'count': new_count})

    def put(self, request):
        """Legacy support — endi server o'zi hisoblaydi."""
        return self.post(request)
