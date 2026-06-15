from django.urls import path
from .views import TransactionListCreateView, TransactionDetailView

urlpatterns = [
    path('', TransactionListCreateView.as_view()),
    path('<int:pk>/', TransactionDetailView.as_view()),
]
