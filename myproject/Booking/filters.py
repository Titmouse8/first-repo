import django_filters
from .models import MenuItem, Order
from rest_framework import filters


# class StatusPendingFilterBackend(filters.BaseFilterBackend):
#     #vyfiltruje len polozky kt maju status pending
#     def filter_queryset(self, request, queryset, view):
#         return queryset.filter(status='PENDING')        #if we use queryset.exclude() instead of filter we get oposite result - every item except the one with status pending



class MenuItemFilter(django_filters.FilterSet):
    class Meta:
        model = MenuItem
        fields = {
            'price': ['exact', 'lt', 'gt', 'range'],          #list of lookups contains znamena ze dostaneme queryset kt. obsahuje cast hladaneho vyrazu; icontains pre case-insensitive
            'item_name': ['exact', 'icontains']
        }


class OrderFilter(django_filters.FilterSet):
    created_at = django_filters.DateFilter(field_name='created_at__date')   #to excract date component from datetime format, aby sme mohli vyhladavat podla konkretneho datumu aôe nemuseli uvadzat cas 
    # napr ak chceme najst objednavky z 4.12 tak by nam nic nenaslo lebo kazda bola vytvorena v inom case preho chceme dostat z fieldu iba datum podla kt budeme filtrovat
    class Meta:
        model = Order
        fields = {
            'status': ['exact'],
            'created_at': ['lt', 'gt', 'exact']
        }