from rest_framework import serializers
from .models import Category,MenuItem,Cart,Order,OrderItem
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    category = CategorySerializer(read_only=True)
    class Meta:
        model = MenuItem
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'username', 'password')

        extra_kwargs = {'password': {'write_only': True}}

class CartSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        attrs['price'] = attrs['quantity'] * attrs['unit_price']
        return attrs
    class Meta:
        model = Cart
        fields = '__all__'

        read_only_fields = ["user", "price"]

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ('id', 'user', 'delivery_crew', 'status', 'total', 'date', 'order_items')

        read_only_fields = ["user", "date", "total"]

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('status',) 

