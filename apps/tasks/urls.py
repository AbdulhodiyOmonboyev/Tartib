from django.urls import path
from .views import TaskListCreateView, TaskDetailView

urlpatterns = [
    path('', TaskListCreateView.as_view()),
    path('<int:pk>/', TaskDetailView.as_view()),
]
