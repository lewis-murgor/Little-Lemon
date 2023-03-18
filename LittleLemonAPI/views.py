from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from .models import Category,MenuItem,Cart,Order,OrderItem
from .serializers import CategorySerializer,MenuItemSerializer
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class MenuItemsView(APIView):
    def get(self, request):
        queryset = MenuItem.objects.all()
        serializers = MenuItemSerializer(queryset, many=True)
        return Response(serializers.data)
    
    def post(self, request):
        if request.user.groups.filter(name='Manager').exists():
            serializers = MenuItemSerializer(data=request.data)
            if serializers.is_valid():
                serializers.save()
                return Response(serializers.data, status=status.HTTP_201_CREATED)
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"You are not authorized"}, status=status.HTTP_401_UNAUTHORIZED)
