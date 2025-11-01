from django.db import models
from django.contrib.auth.models import User, AbstractUser
import uuid
# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.category_name

class MenuItem(models.Model):
    item_name = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(max_length=200)
    def __str__(self):
        return self.item_name
    class Meta():
        db_table = "Menu"

class Order(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "pending"
        CONFIRMED = "confirmed"
        CANCELLED = "cancelled"
    
    order_id = models.BigAutoField(primary_key=True)
    # A UUID (Universally Unique Identifier) is a 128-bit value designed to provide a globally unique identifier. 
    # It's commonly used for identifying entities across various systems and databases, ensuring that each identifier is distinct. 
    user = models.ForeignKey(User, on_delete=models.CASCADE,)
    delivery_crew = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='delivery_crew', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices = StatusChoices.choices,
        default= StatusChoices.PENDING
    )
    menuitems = models.ManyToManyField(MenuItem, through='OrderItem', related_name='orders')

    def __str__(self):
        return f'Order {self.order_id} created by {self.user}'

    

class OrderItem(models.Model):
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    #related name funguje ak chceme dostať druhú stranu vzťahu - OrderItem.order - dosteneme objednávku kt prislúcha k danému orderitem
    #order.items.all() - dostaneme všetky orderitem v danej objednavke
    quantity = models.PositiveSmallIntegerField()

    @property
    def item_subtotal(self):
        return self.menuitem.price * self.quantity
    
    def __str__(self):
        return f"{self.quantity} x {self.menuitem.item_name} in order {self.order.order_id}"
    


class Booking(models.Model):
    name = models.CharField(max_length=20)
    reservation_date = models.DateField()
    reservation_slot = models.SmallIntegerField(default=10)
    def __str__(self):
        return self.name  


# class User(AbstractUser):
#     # create field for users to upload their curriculum vitae, upload_to - directory where cv will be saved, null=True-because we allready have users, blank=True-its optional
#     cv = models.FileField(upload_to='cvs/', null=True, blank=True)
