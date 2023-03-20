from django.shortcuts import render
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from .models import Category,MenuItem,Cart,Order,OrderItem
from .serializers import CategorySerializer,MenuItemSerializer,UserSerializer
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token 
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class MenuItemsView(APIView):
    def get(self, request, format=None):
        queryset = MenuItem.objects.all()
        serializers = MenuItemSerializer(queryset, many=True)
        return Response(serializers.data)
    
    def post(self, request, format=None):
        if request.user.groups.filter(name='Manager').exists():
            serializers = MenuItemSerializer(data=request.data)
            if serializers.is_valid():
                serializers.save()
                return Response(serializers.data, status=status.HTTP_201_CREATED)
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"You are not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

class MenuItemView(APIView):
    def get_menuitem(self, pk):
        try:
            return  MenuItem.objects.get(pk=pk)
        except MenuItem.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        menuitem = self.get_menuitem(pk)
        serializers = MenuItemSerializer(menuitem)
        return Response(serializers.data)
    
    def put(self, request, pk, format=None):
        if request.user.groups.filter(name='Manager').exists():
            menuitem = self.get_menuitem(pk)
            serializers = MenuItemSerializer(menuitem, data=request.data)
            if serializers.is_valid():
                serializers.save()
                return Response(serializers.data)
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"You are not authorized"}, status=status.HTTP_401_UNAUTHORIZED)
    
    def patch(self, request, pk, format=None):
        if request.user.groups.filter(name='Manager').exists():
            menuitem = self.get_menuitem(pk)
            serializers = MenuItemSerializer(menuitem, data=request.data, partial=True)
            if serializers.is_valid():
                serializers.save()
                return Response(serializers.data)
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"You are not authorized"}, status=status.HTTP_401_UNAUTHORIZED)
    
    def delete(self, request, pk, format=None):
        if request.user.groups.filter(name='Manager').exists():
            menuitem = self.get_menuitem(pk)
            menuitem.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"message":"You are not authorized"}, status=status.HTTP_401_UNAUTHORIZED)
    
class ManagerView(APIView):
    def get(self, request, format=None):
        if request.user.groups.filter(name='Manager').exists():
            queryset = User.objects.filter(groups__name='Manager')
            serializers = UserSerializer(queryset, many=True)
            return Response(serializers.data)
        return Response({"message":"You are not authorized"}, status=status.HTTP_401_UNAUTHORIZED)
    
    def post(self, request, format=None):
        if request.user.groups.filter(name='Manager').exists():
            serializers = UserSerializer(data=request.data)
            data = {}
            manager = Group.objects.get(name='Manager') 
            if serializers.is_valid():
                manager.user_set.add(serializers)
                serializers.save()
                user = User.objects.get(username=serializers.data['username'])
                token = Token.objects.create(user=user).key
                data['token'] = token
            else:
                data = serializers.errors
            return Response(serializers.data, status=status.HTTP_201_CREATED)
                #return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"You are not authorized"}, status=status.HTTP_401_UNAUTHORIZED)
