import json
from datetime import datetime

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
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
from rest_framework.throttling import ScopedRateThrottle

from templates import *

from .filters import MenuItemFilter, OrderFilter #StatusPendingFilterBackend
from .forms import BookingForm
from .models import *
from .permissions import IsManager, IsOwner
from .serializers import *
from .tasks import send_order_confirmation_email

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

    @method_decorator(cache_page(60 * 15, key_prefix="menuitem_list"))   # sec * min =15min - to znamena ze ked sa stranka ulozi do cache tak v priebehu 15 min sa bude zbrazovat tak ako sa ulozila
    #ak sa medzitym nejake data zmenia uvidime to az po 15min; key_prefix=""-tento prefix budu mat vsetky caches ulozene v container v redis ktore pochedzaju z tejto list() method
    #response to every URL passed to this list method will be cached and stored in redis, if url changed e.g. to menu-item/?ordering=name objects sa znova natiahnu z dtab. ale potom ulozia do cache
    #za kazdym ked sa trochu zmeni URL tak sa objects najprv tahaju z datab. a potom sa ulozia do cache a ked refreshneme uz dostaneme data z cache
    def list(self, request, *args, **kwargs):   #nejdeme nic prepisovat v list method potrebujeme ju definovat len aby sme na nu mohli pouzit decorator
        return super().list(request, *args, **kwargs)
    

    def get_queryset(self):
        #get queryset is responsible for getting objects from database, when we delay it so we can see if object came from database or cache
        import time
        time.sleep(2)
        return super().get_queryset()


    


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
    throttle_scope = 'order'
    throttle_classes = [ScopedRateThrottle]
    queryset = Order.objects.prefetch_related('items__menuitem', 'user').all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend]
    pagination_class = None

    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)
    # serializer.save() can be use to pass additional attributes to the save method
    # perform_create is method on model viewset, can be use if we need to pass additional arguments to serializer save method
    # we can overwrite it and pass custom data - chceme aby user nebol zadavany uzivatelom pri vytvoreni objednavky ale automaticky bol priradeny uzivatel kt je prihlaseny
        send_order_confirmation_email.delay(order.order_id, self.request.user.email)

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
    
    @method_decorator(cache_page(60 * 15, key_prefix="order_list"))
    @method_decorator(vary_on_headers("Authorization"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    # Vary Headers - control caching based on specific request headers, ked pouzijeme cache_page tak mame caching na zaklade URL ale pri /orders dostaneme list of orders
    # pre konkretneho pouzivatela kt. Bearer Token je pouzity v Header, ak mame cache stranky a zmeni sa pouzivatel tak stale budeme mat stranku z cache - predchadzajuceho 
    # pouzivatela lebo URL sa nezmenilo, zmenil sa Header(konkretne token), takze potrebujeme caching na zaklade zmien v Headers - aby sme rozoznaly users lebo url je rovnaka
    # you can also use Vary header to tell caching mechanism that the page output depends on cookie or language(vary on language)
    # PROBLEM token used in authorization will be changed often(depends on JWT token lifetime) - lots of caches for the same user - every time access token will expire new cache 
    # to invalidate cache for specific user will be problem becouse we cannot access token from request



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

class UserCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticated]



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
