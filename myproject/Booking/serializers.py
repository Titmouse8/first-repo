from .models import *
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from django.db import transaction


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
        fields = ['username', 'password', 'email']


class OrderItemSerializer(serializers.ModelSerializer):
    #user = serializers.ReadOnlyField(source='user.username')
    menuitem_name = serializers.CharField(source='menuitem.item_name')
    menuitem_price = serializers.DecimalField(source='menuitem.price', max_digits=5, decimal_places=2)
    class Meta:
        model = OrderItem
        fields = ['menuitem_name', 'menuitem_price', 'quantity', 'item_subtotal']


class OrderSerializer(serializers.ModelSerializer):
    #items - OrderItemSerializer is nested serializer but is read only, if we want POST we cannot use OrderSerializer to create items in order
    user = serializers.StringRelatedField()
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name='total')

    def total(self, obj):
        order_items = obj.items.all()   # dostaneme všetky items v danej objednávke, obj = Order
        return sum(order_item.item_subtotal for order_item in order_items)
    
    class Meta:
        model = Order
        fields = ['order_id', 'user', 'created_at', 'status', 'delivery_crew', 'items', 'total_price']
    

# Writeble nested representations
class OrderCreateSerializer(serializers.ModelSerializer):
    #nested serializer for creating order
    class OrderItemCreateSerializer(serializers.ModelSerializer):
        # to create item inside of order
        class Meta:
            model = OrderItem
            fields = ['menuitem', 'quantity']
    items = OrderItemCreateSerializer(many=True, required=False)    #we set required to false so we can update order without defining items again 
    #if we want to change only order and not orderitem -nejak to nefunguje

    def create(self, validated_data):
        #we need to overwrite create method to tell the serializer how he should create these nested items
        #we extract orderitem_data from validated_data(dict.) and we pop out items from that - so we take items instance to pop it out of dictionary
        orderitem_data = validated_data.pop('items')
        #now we create order itself - order can be created without orderitems, we pass validated_data after we pop-out items because order model
        # dont have items all we need to create in Order model is status, delivery_crew lebo vo validated_data su vsetky data a my z nich pop-out vyberieme menuitem a quantity
        # a ostane nam status, delivery crew; vlastne sme rozdelili tie data z polovice vz Order z druhej OrderItem
        with transaction.atomic():      #taktiez pouzijeme transaction lebo nema zmysel vytvorit obj bez items
            order = Order.objects.create(**validated_data)
            #now we create items
            for item in orderitem_data:
                OrderItem.objects.create(order=order, **item)      #we associate each orderitem with order that was created in line above, 
                # **item comes from loop and its syntax to get data (**kwargs)
        return order
    
    def update(self, instance, validated_data):
        #as arguments takes validated_data same as create but also instance because we updated so object must already exist
        #we again pop-out orderitem data for orderitem instance
        orderitem_data = validated_data.pop('items')
        # then update instance - update order itself for example status not child orderitem
        with transaction.atomic():
        # transaction.atomic nam zabespeci ze bud prebehne vsetko co je zabalene pod nim alebo nic, je to preto aby sa nestalo ze sa vymazu stare items ale nevytvoria nove
            instance = super().update(instance, validated_data)
            # check if orderitem data was pass, if yes - delete old data and create new orderitem object
            if orderitem_data is not None:
                instance.items.all().delete()
                for item in orderitem_data:
                    OrderItem.objects.create(order=instance, **item)    #order=instance -we match orderitem with order kt teraz predstavuje instance kt sme updately
        return instance


    class Meta:
        model = Order
        fields = ['order_id', 'user', 'status', 'delivery_crew', 'items']    #'total_price'
        extra_kwargs = {
            'user': {'read_only': True}     #dalsi spôsob ako vytvorit read_only field
        }

    
#generic serializer that can represent any data not specifically model data
class MenuItemInfoSerializer(serializers.Serializer):
    menuitems = MenuItemSerializer(many=True)
    count = serializers.IntegerField()
    max_price = serializers.FloatField()


#class BookingSerializer(serializers.Serializer):
    #class Meta:
        #model = Booking
        #fields = '__all__'