import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import lorem_ipsum
from Booking.models import *
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Create database data"

    def handle(self, *args, **kwargs):
        #get superuser
        user = User.objects.filter(username="rest_admin").first()

        #create categories
        categories = [
            Category(category_name="Soup"),
            Category(category_name="Main Dish"),
            Category(category_name="Dessert"),
            Category(category_name="Drink"),
        ]
        Category.objects.bulk_create(categories)
        categories = Category.objects.all()

        #create menuitems - name, category, price, description
        menu_items = [
            MenuItem(item_name="Beef roast", category= categories[1], price=Decimal('16.50'), description=lorem_ipsum.sentence()),
            MenuItem(item_name="Tomato soup", category= categories[0], price=Decimal('4.30'), description=lorem_ipsum.sentence()),
            MenuItem(item_name="Tirmissu", category= categories[2], price=Decimal('5.00'), description=lorem_ipsum.sentence()),
            MenuItem(item_name="Mojito", category= categories[3], price=Decimal('6.10'), description=lorem_ipsum.sentence()),
        ]
        MenuItem.objects.bulk_create(menu_items)
        menu_items = MenuItem.objects.all()

        #create orders tied to the superuser

        for _ in range(3):
            #create order with 2 orderitems
            order = Order.objects.create(user=user)
            for menuitem in random.sample(list(menu_items), 2):
                OrderItem.objects.create(order=order, menuitem=menuitem, quantity=random.randint(1,3))