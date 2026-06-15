from django.urls import path
from .views import CategoryListCreateView, CategoryDeleteView

urlpatterns = [
    path('', CategoryListCreateView.as_view()),
    path('<str:name>/', CategoryDeleteView.as_view()),
]
