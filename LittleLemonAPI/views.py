from django.shortcuts import render
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics, permissions
from .permissions import IsManager
from rest_framework.views import APIView
from .models import Category,MenuItem,Cart,Order,OrderItem
from .serializers import CategorySerializer,MenuItemSerializer,UserSerializer,CartSerializer,OrderSerializer,OrderItemSerializer,OrderStatusSerializer
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token 
from rest_framework.permissions import IsAuthenticated
#from rest_framework.filters import OrderingFilter
#from rest_framework.pagination import PageNumberPagination
#from django_filters.rest_framework import DjangoFilterBackend

# Create your views here.
class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return MenuItem.objects.all()
    
    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [IsManager]
        return super(MenuItemsView, self).get_permissions()

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
                return Response({"message":"success"}, status=status.HTTP_200_OK)
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

class SingleDeliveryCrewView(APIView):
    def get_delivery_crew(self, pk):
        try:
            return  User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404
        
    def delete(self, request, pk, format=None):
        if request.user.groups.filter(name='Manager').exists():
            delivery_crew = self.get_delivery_crew(pk)
            group = Group.objects.get(name='Delivery crew')
            if delivery_crew.groups.filter(name='Delivery crew').exists():
                delivery_crew.groups.remove(group)
                return Response({"message":"success"}, status=status.HTTP_200_OK)
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response({"message":"You are not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

class CartView(APIView):
    def get(self, request):
        queryset = Cart.objects.all().filter(user=self.request.user)
        serializers = CartSerializer(queryset, many=True)
        return Response(serializers.data)
    
    def post(self, request):
        serializers = CartSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save(user=self.request.user)
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        cart = Cart.objects.all().filter(user=self.request.user)
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class OrderView(APIView):
    def get(self, request, format=None):
        if request.user.groups.filter(name='Manager').exists():
            orders = Order.objects.all()
            orders_data = []
            for order in orders:
                order_items = OrderItem.objects.filter(order=order)
                serializer = OrderSerializer({'order':order, 'order_items':order_items})
                orders_data.append(serializer.data)
            return Response(orders_data)
        elif request.user.groups.filter(name='Delivery crew').exists():
            user = request.user
            orders = Order.objects.filter(delivery_crew=user)
            order_data = []
            for order in orders:
                order_items = OrderItem.objects.filter(order=order)
                serializers = OrderSerializer({'order':order, 'order_items': order_items})
                order_data.append(serializers.data)
            return Response(order_data)
        else:
            queryset = Order.objects.all().filter(user=self.request.user)
            order_data = []
            for order in queryset:
                order_items = OrderItem.objects.filter(order=order)
                serializer = OrderSerializer({'order':order, 'order_items': order_items})
                order_data.append(serializer.data)
            return Response(order_data)

    def post(self, request):
        user = request.user
        cart_items = Cart.objects.filter(user=user)
        order_items = []
        for item in cart_items:
            order_item = OrderItem()
            order_item.order = Order.objects.create(user=user, total=item.menuitem.price * item.quantity)
            order_item.menuitem = item.menuitem
            order_item.quantity = item.quantity
            order_item.unit_price = item.unit_price
            order_item.price = item.price
            order_item.save()
            order_items.append(order_item)
        cart_items.delete()
        return Response({'message': 'Your order has been created.'}, status=status.HTTP_201_CREATED)


class SingleOrderView(APIView):
    def get_order(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            raise Http404
        
    def get(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, user=self.request.user)
        except Order.DoesNotExist:
            return Response({'message': 'You do not have permission to access this order'}, status=status.HTTP_403_FORBIDDEN)
        order_items = OrderItem.objects.filter(order=order)
        serializer = OrderItemSerializer(order_items, many=True)
        return Response(serializer.data)
    
    def put(self, request, pk):
        if request.user.groups.filter(name='Manager').exists():
            order = self.get_order(pk)
            serializers = OrderSerializer(order, data=request.data)
            if serializers.is_valid():
                serializers.save()
                return Response(serializers.data)
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"You are not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

    def patch(self, request, pk):
        if request.user.groups.filter(name='Manager').exists():
            order = self.get_order(pk)
            serializers = OrderSerializer(order, data=request.data, partial=True)
            if serializers.is_valid():
                serializers.save()
                return Response(serializers.data)
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.user.groups.filter(name='Delivery crew').exists():
            order = Order.objects.filter(delivery_crew=request.user, pk=pk).first()
            if not order:
                return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = OrderStatusSerializer(order, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"You are not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, pk):
        if request.user.groups.filter(name='Manager').exists():
            order = self.get_order(pk)
            order.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"message":"You are not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

