from django.contrib import admin
from .models import *
# Register your models here.


class OrderItemInline(admin.TabularInline):
    #allows you attach a related object (orderitem) when we creating order itself (parent object)
    model = OrderItem

class OrderAdmin(admin.ModelAdmin):
    # adding inlines so we can add orderitems dynamicly to the order on admin page
    inlines = [
        OrderItemInline
    ]


admin.site.register(Category)
admin.site.register(MenuItem)
admin.site.register(Order, OrderAdmin)
#admin.site.register(OrderItem)
