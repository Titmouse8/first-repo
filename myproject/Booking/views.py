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
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.views import APIView
from django.utils.timezone import localdate, datetime
from django.http import JsonResponse
from django.core import serializers
from datetime import datetime
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .forms import BookingForm
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from .filters import MenuItemFilter
# Create your views here.

def index(request):
    return render(request, 'index.html', {})

class CategoryView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.prefetch_related('category')
    serializer_class = MenuItemSerializer
    #permission_classes = [IsManager,]
    filterset_class = MenuItemFilter
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['=item_name', 'description', 'category__category_name']        #case insensitive partial matching filter, search across given fields using ?search= , 
    #if you use = with field name: =item_name return only exact match with search filter
    ordering_fields = ['item_name', 'price']
    def get_permissions(self):
        permission_classes = [AllowAny]
        if self.request.method != 'GET':
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    


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


class MenuitemInfo(APIView):
    def get(self, request):
        menuitems = MenuItem.objects.all()
        serializer = MenuItemInfoSerializer({
            'menuitems': menuitems,
            'count': len(menuitems),
            'max_price': menuitems.aggregate(max_price=Max('price'))['max_price']
        }
        )
        return Response(serializer.data)



def reservations(request):
    bookings = Booking.objects.all()
    booking_json = serializers.serialize('json', bookings)
    return render(request, 'bookings.html', {'bookings': booking_json})

def book(request):
    book = BookingForm()
    if request.method == 'POST':
        book = BookingForm(request.POST)
        if book.is_valid():
            cd = book.cleaned_data
            new_book = Booking(
                name = cd['name'],
                reservation_date = cd['date'],
                reservation_slot = cd['time'],
            )
            new_book.save()
    return render(request, 'book.html', {'book_form': book})

@csrf_exempt
def bookings(request):
    if request.method == 'POST':
        data = json.load(request)
        exist = Booking.objects.filter(reservation_date = data['reservation_date']).filter(reservation_slot = data['reservation_slot']).exists()
        if exist == False:
            booking = Booking(
                name = data['name'],
                reservation_date = data['reservation_date'],
                reservation_slot = data['reservation_slot'],
            )
            booking.save()
        else:
            return HttpResponse("{'error':1}", content_type = 'application/json')
    
    date = request.GET.get('date', datetime.today().date())
    bookings = Booking.objects.all().filter(reservation_date = date)
    bookings_json = serializers.serialize('json', bookings)
    #return render(request, 'booking.html', {'bookings': bookings_json})
    return HttpResponse(bookings_json, content_type = 'application/json')
