import django_filters
from .models import MenuItem

class MenuItemFilter(django_filters.FilterSet):
    class Meta:
        model = MenuItem
        fields = {
            'price': ['exact', 'lt', 'gt', 'range'],          #list of lookups contains znamena ze dostaneme queryset kt. obsahuje cast hladaneho vyrazu; icontains pre case-insensitive
            'item_name': ['exact', 'icontains']
        }