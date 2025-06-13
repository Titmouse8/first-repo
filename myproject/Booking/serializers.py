from .models import *
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer
    class Meta:
        model = MenuItem
        fields = ['id', 'item_name', 'category', 'price', 'description']
        extra_kwargs = {
            'price': {'min_value': 0},
            'title': {'validators': [UniqueValidator(queryset=MenuItem.objects.all())]},
        }

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer
    class Meta:
        model = Order
        fields = ['id', 'user', 'date', 'status', 'delivery_crew']

class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer
    order = OrderSerializer
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = OrderItem
        fields = ['id', 'menuitem', 'quantity', 'order', 'item_subtotal', 'user']
