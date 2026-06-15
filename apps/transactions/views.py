from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Transaction
from .serializers import TransactionSerializer


class TransactionListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        txs = Transaction.objects.filter(user=request.user)
        return Response(TransactionSerializer(txs, many=True).data)

    def post(self, request):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'message': list(serializer.errors.values())[0][0]},
                        status=status.HTTP_400_BAD_REQUEST)


class TransactionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Transaction.objects.get(pk=pk, user=user)
        except Transaction.DoesNotExist:
            return None

    def put(self, request, pk):
        tx = self.get_object(pk, request.user)
        if not tx:
            return Response({'message': 'Topilmadi'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TransactionSerializer(tx, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({'message': list(serializer.errors.values())[0][0]},
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        tx = self.get_object(pk, request.user)
        if not tx:
            return Response({'message': 'Topilmadi'}, status=status.HTTP_404_NOT_FOUND)
        tx.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
