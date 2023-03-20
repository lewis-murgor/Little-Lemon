from rest_framework import serializers
from .models import Category,MenuItem,Cart,Order,OrderItem
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(
        style={"input_type": "password"}, write_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password', 'password2')

        def save(self):
            user = User(
            email=self.validated_data['email'],
            username=self.validated_data['username'],

            )
            password = self.validated_data['password']
            password2 = self.validated_data['password2']

            if password != password2:
                raise serializers.ValidationError(
                    {'password': 'Passwords do not match.'})
            user.set_password(password)
            user.save()
            return user
