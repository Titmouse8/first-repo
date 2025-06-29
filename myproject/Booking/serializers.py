from .models import *
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_name']
        extra_kwargs = {
            'category_name': {'validators': [UniqueValidator(queryset=Category.objects.all())]},
        }

#class MenuItemSerializer(serializers.ModelSerializer):
    #category = CategorySerializer
    #category = serializers.StringRelatedField()
    #category_name = serializers.CharField(source='category.category_name', read_only=True)
    #class Meta:
        #model = MenuItem
        #fields = ['id', 'item_name', 'category', 'category_name', 'price', 'description']
        #extra_kwargs = {
            #'price': {'min_value': 0.00},
            #'item_name': {'validators': [UniqueValidator(queryset=MenuItem.objects.all())]},
        #}


class MenuItemSerializer(serializers.ModelSerializer):
    # Tu očakávame meno kategórie ako vstup a zobrazíme ho aj ako výstup
    category = serializers.CharField()

    class Meta:
        model = MenuItem
        fields = ['id', 'item_name', 'category', 'price', 'description']
        extra_kwargs = {
            'price': {'min_value': 0.00},
            'item_name': {
                'validators': [UniqueValidator(queryset=MenuItem.objects.all())]
            },
        }

    def create(self, validated_data):
        category_name = validated_data.pop('category')
        try:
            category = Category.objects.get(category_name=category_name)
        except Category.DoesNotExist:
            raise serializers.ValidationError({'category': 'Category not found.'})

        validated_data['category'] = category
        return super().create(validated_data)

    def update(self, instance, validated_data):
        category_name = validated_data.pop('category', None)
        if category_name:
            try:
                category = Category.objects.get(category_name=category_name)
            except Category.DoesNotExist:
                raise serializers.ValidationError({'category': 'Category not found.'})
            validated_data['category'] = category

        return super().update(instance, validated_data)

        

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    #user = serializers.ReadOnlyField(source='user.username')
    menuitem_name = serializers.CharField(source='menuitem.item_name')
    menuitem_price = serializers.DecimalField(source='menuitem.price', max_digits=5, decimal_places=2)
    class Meta:
        model = OrderItem
        fields = ['menuitem_name', 'menuitem_price', 'quantity', 'item_subtotal']


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name='total')

    def total(self, obj):
        order_items = obj.items.all()   # dostaneme všetky items v danej objednávke, obj = Order
        return sum(order_item.item_subtotal for order_item in order_items)
    
    class Meta:
        model = Order
        fields = ['order_id', 'user', 'created_at', 'status', 'delivery_crew', 'items', 'total_price']
    

    
#generic serializer that can represent any data not specifically model data
class MenuItemInfoSerializer(serializers.Serializer):
    menuitems = MenuItemSerializer(many=True)
    count = serializers.IntegerField()
    max_price = serializers.FloatField()


#class BookingSerializer(serializers.Serializer):
    #class Meta:
        #model = Booking
        #fields = '__all__'