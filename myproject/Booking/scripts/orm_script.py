from Booking.models import *
from django.db import connection
from pprint import pprint
import random
from django.db.models.functions import Upper, Length, Concat
from django.db.models import Count, Avg, Min, Max, Sum, StdDev, Variance, CharField, Value
from django.utils import timezone

def run():
    #order = Order.objects.first()
    #menuitem = order.menuitems.all()
    #print(menuitem)

    #pridáme mojito do objednávky č.4
    #menuitem = MenuItem.objects.last()
    #order = Order.objects.get(pk=4)
    #OrderItem.objects.create(
        #menuitem=menuitem, order=order, quantity=1
    #)
    
    # vypíše nám množstvá produktov v obj. 2
    #order = Order.objects.get(pk=2)
    #items_in_order = OrderItem.objects.filter(order=order)
    #for i in items_in_order:
        #print(i.quantity)

    #pridanie menuitems do obj. cez add()
    #order = Order.objects.get(pk=3)
    #menuitem = MenuItem.objects.first()
    #order.menuitems.add(menuitem, through_defaults={'quantity': 3})
    # pozrieme či ho pridalo:
    #items = OrderItem.objects.filter(order=order)
    #for i in items:
        #print(i.quantity)
        #print(i.menuitem.item_name)
    
    #vytvoríme novu obj. a pridáme jej prvých 5 menuitems s nahodnými množstvami
    #user = User.objects.first()
    #Order.objects.create(user=user, status=Order.StatusChoices.PENDING)
    #order = Order.objects.last()
    #order.menuitems.set(
        #MenuItem.objects.all()[:5],
        #through_defaults={'quantity': random.randint(1,5)}
    #)   # na obj nastavíme menuitems a cez through_defaults zvolíme množstvá



    # values() vráti dictionary! nie Queryset z modelu iba so stlpcami ktoré zadefinujeme, možeme s ním pracovať ako s obč dictionary
    #menuitems = MenuItem.objects.values('item_name', 'price')
    #print(menuitems)

    #values() can takes additional keywords (for functions) from django.db.models.functions - will fetch data from db and apply function on them
    #menuitems = MenuItem.objects.values(name_upper=Upper('item_name'))[:2]
    #print(menuitems)
    #print(connection.queries)   #will show what raw queries was called on sql


    #values_list() returns tuples
    #menuitems = MenuItem.objects.values_list('item_name','category__category_name')
    #menuitems = MenuItem.objects.values_list('item_name', flat=True)   #if we use only 1 argument we can use kw flat and instead tuple we get list
    #print(menuitems)


    # aggregation - brings multiple values into single value, returns dictionary
    # aggregation is a terminal clause, additional functions like filter must be provided before aggregation(aggreg je vzdy na konci)
    # aggregation functions: Count, Avg, Max, Min, Sum

    #print(MenuItem.objects.filter(item_name__startswith='M').count())
    #print(MenuItem.objects.aggregate(total=Count('id')))
    #print(MenuItem.objects.aggregate(avg=Avg('price')))
    #print(MenuItem.objects.aggregate(min=Min('price'), max=Max('price'), sum=Sum('price')))


    # vypočíta súčet všetkých predaných položkách v objednávkach za minulý mesiac - z minulý mesiac sa predalo jedlo za 82.10€
    #one_month_ago = timezone.now() - timezone.timedelta(days=31)
    #orders = Order.objects.filter(created_at__gte=one_month_ago)        # __gte = greater than or equale
    #print(orders.aggregate(sum=Sum('menuitems__price')))



    # annotation - you get added value to each item in QuerySet you annotating
    
    #fetch all menuitems and we want to get the number of characters in each name
    # menuitem has not length attribute - was annotate - there was added new info
    #menuitems = MenuItem.objects.annotate(length=Length('item_name')).filter(
        #length__gt=10   #we can use filter with annotate so we get only items with more than 10 letters
    #)
    #print(menuitems.first().length)
    #print(menuitems.values('item_name', 'length'))   #now we can use values(), as if 'length' was attribute 


    # we want to display all sales
    #orders = Order.objects.annotate(total_price=Sum('menuitems__price')).values(
        #'total_price'   # so we get only total_price from db and no everything - less queries to db
    #)
    #print([r['total_price'] for r in orders])   #musíme použiť r[' '] lebo order dostaneme ako dictionary
    #pprint(connection.queries)



    # count menuitems in each category - najprv rozdelí items do kategorií a potom spočíta items v každej kategorii
    # you can also use .order_by(' ') - pre zoradenie vysledkov(mozme použiť znamienko -)
    # or .filter(item_count__lt = 5) - less than
    menuitems = MenuItem.objects.values('category').annotate(item_count=Count('item_name'))
    print([m['item_count']for m in menuitems])
    print(menuitems)