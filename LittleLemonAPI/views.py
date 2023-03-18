from django.shortcuts import render
from rest_framework import generics
from .models import Category,MenuItem,Cart,Order,OrderItem
from .serializers import CategorySerializer,MenuItemSerializer
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class MenuItemsView(generics.ListAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
