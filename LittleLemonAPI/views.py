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
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

# Create your views here.
class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class MenuItemsView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['category', 'price']
    ordering_fields = ['price']
    search_fields = ['title', 'category__title']

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
        if request.user.groups.filter(name='Manager').exists() or request.user.is_staff:
            queryset = User.objects.filter(groups__name='Manager')
            serializers = UserSerializer(queryset, many=True)
            return Response(serializers.data)
        return Response({"message":"You are not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        username = request.data.get('username')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404
        if request.user.groups.filter(name='Manager').exists() or request.user.is_staff:
            manager_group = Group.objects.get(name='Manager')
            user.groups.add(manager_group)
            return Response({'message': f'{username} has been added to the manager group.'}, status=status.HTTP_201_CREATED)

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
        if request.user.groups.filter(name='Manager').exists() or request.user.is_staff:
            queryset = User.objects.filter(groups__name='Delivery crew')
            serializers = UserSerializer(queryset, many=True)
            return Response(serializers.data)
        return Response({"message":"You are not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        username = request.data.get('username')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404
        
        if request.user.groups.filter(name='Manager').exists() or request.user.is_staff:
            delivery_crew_group = Group.objects.get(name='Delivery crew')
            user.groups.add(delivery_crew_group)
            return Response({'message': f'{username} has been added to the delivery crew group.'}, status=status.HTTP_201_CREATED)

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

class OrderView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['status']
    ordering_fields = ['date']

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.all().prefetch_related('order_items')
        elif user.groups.filter(name='Delivery crew').exists():
            return Order.objects.filter(delivery_crew=user).prefetch_related('order_items')
        return Order.objects.filter(user=user).prefetch_related('order_items')
    
    def create(self, request, *args, **kwargs):
        user = request.user
        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            return Response({"error": "No items in cart"}, status=status.HTTP_404_NOT_FOUND)
        
        order_items = []
        for item in cart_items:
            order_item = OrderItem()
            order_item.order = Order.objects.create(user=user, total=item.menuitem.price * item.quantity)
            order_item.menuitem = item.menuitem
            order_item.quantity = item.quantity
            order_item.unit_price = item.unit_price
            order_item.price = item.price
            order_items.append(order_item)
        OrderItem.objects.bulk_create(order_items)
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

