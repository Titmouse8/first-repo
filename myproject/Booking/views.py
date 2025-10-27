import json
from datetime import datetime

from django.contrib.auth.models import Group, User
from django.core import serializers
from django.db.models import Max
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.timezone import datetime, localdate
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from templates import *

from .filters import MenuItemFilter, OrderFilter #StatusPendingFilterBackend
from .forms import BookingForm
from .models import *
from .permissions import IsManager, IsOwner
from .serializers import *

# Create your views here.

def index(request):
    return render(request, 'index.html', {})

class CategoryView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend]

class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.prefetch_related('category').order_by('pk')
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
    #we can overwrite pagination class for given view:
    pagination_class = PageNumberPagination
    pagination_class.page_size = 3 
    pagination_class.page_size_query_param = 'page_size'
    pagination_class.max_page_size = 10 


    


class MenuItemSingleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    lookup_url_kwarg = 'product_id'
    permission_classes = [IsManager,]

class OrderItemSingleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsOwner,]


class OrderViewSet(viewsets.ModelViewSet):
    #all orders
    queryset = Order.objects.prefetch_related('items__menuitem', 'user').all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend]
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    # serializer.save() can be use to pass additional attributes to the save method
    # perform_create is method on model viewset, can be use if we need to pass additional arguments to serializer save method
    # we can overwrite it and pass custom data - chceme aby user nebol zadavany uzivatelom pri vytvoreni objednavky ale automaticky bol priradeny uzivatel kt je prihlaseny

    def get_serializer_class(self):
        # if it is create action (post) we use OrderCreateSerializer otherwise we use OrderSerializer
        # can also check if post: if self.request.method == 'POST'
        if self.action == 'create' or self.action == 'update':
            return OrderCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs

    #nepotrebujeme uz action definovane nizsie lebo sme prepisali get_queryset a to zabespeci ze kazdy zakaznik uvidi iba svoje objednavky
    # @action(detail=False, methods=['get'], url_path='user-orders')
    # #our custom action to get only user's own orders; detail=False because we getting list(queryset) not single modul
    # def user_orders(self, request):
    #     orders = self.get_queryset().filter(user=request.user)
    #     serializer = self.get_serializer(orders, many=True)
    #     return Response(serializer.data)


# class OrderView(generics.ListCreateAPIView):
#     queryset = Order.objects.prefetch_related('items__menuitem', 'user').all()
#     serializer_class = OrderSerializer
#     filter_backends = [StatusPendingFilterBackend, DjangoFilterBackend]
#     #permission_classes = [IsAuthenticated,]
#     pagination_class = [LimitOffsetPagination]

# class UserOrderView(generics.ListAPIView):
#     #returns only orders created by user itself
#     queryset = Order.objects.prefetch_related('items__menuitem', 'user').all()
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated,]
#     def get_queryset(self):
#         user = self.request.user
#         qs = super().get_queryset()   #dostaneme queryset kt.sme definovali vyššie
#         return qs.filter(user=user)


class OrderItemView(generics.ListCreateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    filter_backends = [DjangoFilterBackend]


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
