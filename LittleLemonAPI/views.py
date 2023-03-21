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

    def post(self, request):
        if request.user.groups.filter(name='Manager').exists():
            serializers = UserSerializer(data=request.data)
            data = {}
            if serializers.is_valid():
                created_user = User.objects.create_user(
                    email = serializers.validated_data['email'],
                    username = serializers.validated_data['username'],
                )
                password = serializers.validated_data['password']
                created_user.set_password(password)
                manager = Group.objects.get(name='Manager')
                created_user.groups.add(manager)
                created_user.save()
                token = Token.objects.create(user=created_user).key
                data['token'] = token
                return Response(serializers.data, status=status.HTTP_201_CREATED)
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"You are not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

class SingleManagerView(APIView):
    def get_manager(self, pk):
        try:
            return  User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404
        
    def delete(self, request, pk, format=None):
        if request.user.groups.filter(name='Manager').exists():
            manager = self.get_manager(pk)
            group = Group.objects.get(name='Manager')
            if manager.groups.filter(name='Manager').exists():
                manager.groups.remove(group)
                return Response(status=status.HTTP_200_OK)
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response({"message":"You are not authorized"}, status=status.HTTP_401_UNAUTHORIZED)
    
class DeliveryCrewView(APIView):
    def get(self, request, format=None):
        if request.user.groups.filter(name='Manager').exists():
            queryset = User.objects.filter(groups__name='Delivery crew')
            serializers = UserSerializer(queryset, many=True)
            return Response(serializers.data)
        return Response({"message":"You are not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        if request.user.groups.filter(name='Manager').exists():
            serializers = UserSerializer(data=request.data)
            data = {}
            if serializers.is_valid():
                created_user = User.objects.create_user(
                    email = serializers.validated_data['email'],
                    username = serializers.validated_data['username'],
                )
                password = serializers.validated_data['password']
                created_user.set_password(password)
                delivery_crew = Group.objects.get(name='Delivery crew')
                created_user.groups.add(delivery_crew)
                created_user.save()
                token = Token.objects.create(user=created_user).key
                data['token'] = token
                return Response(serializers.data, status=status.HTTP_201_CREATED)
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"You are not authorized"}, status=status.HTTP_401_UNAUTHORIZED)
    
    