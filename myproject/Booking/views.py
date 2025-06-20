from django.shortcuts import render, get_object_or_404
from templates import *
from .models import *
from .serializers import *
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User, Group
from django.core import serializers
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from django.db.models import Max
# Create your views here.

def index(request):
    return render(request, 'index.html', {})

class CategoryView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.prefetch_related('category')
    serializer_class = MenuItemSerializer

class MenuItemSingleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    lookup_url_kwarg = 'product_id'

class OrderItemSingleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

class OrderView(generics.ListCreateAPIView):
    queryset = Order.objects.prefetch_related('items__menuitem', 'user').all()
    serializer_class = OrderSerializer

class OrderItemView(generics.ListCreateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

@api_view(['GET'])
def menuitem_info(request):
    menuitems = MenuItem.objects.all()
    serializer = MenuItemInfoSerializer({
        'menuitems': menuitems,
        'count': len(menuitems),
        'max_price': menuitems.aggregate(max_price=Max('price'))['max_price']
    }
    )
    return Response(serializer.data)
