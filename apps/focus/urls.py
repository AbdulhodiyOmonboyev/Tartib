from django.urls import path
from .views import FocusSessionListCreateView, StreakView

urlpatterns = [
    path('sessions/', FocusSessionListCreateView.as_view()),
    path('streak/', StreakView.as_view()),
]
