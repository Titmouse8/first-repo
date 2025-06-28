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
from .permissions import IsManager, IsOwner
from rest_framework.permissions import IsAuthenticated
# Create your views here.

def index(request):
    return render(request, 'index.html', {})

class CategoryView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.prefetch_related('category')
    serializer_class = MenuItemSerializer
    permission_classes = IsManager
    #def get_permissions(self):
        #permission_calsses = []
        #if self.request.method != 'GET':
            #permission_calsses = [IsAuthenticated]
        #return [permission() for permission in permission_calsses]

class MenuItemSingleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    lookup_url_kwarg = 'product_id'
    permission_classes = [IsManager,]

class OrderItemSingleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsOwner,]

class OrderView(generics.ListCreateAPIView):
    queryset = Order.objects.prefetch_related('items__menuitem', 'user').all()
    serializer_class = OrderSerializer
    #permission_classes = [IsAuthenticated,]

class UserOrderView(generics.ListAPIView):
    #returns only orders created by user itself
    queryset = Order.objects.prefetch_related('items__menuitem', 'user').all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated,]
    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()   #dostaneme queryset kt.sme definovali vyššie
        return qs.filter(user=user)


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
