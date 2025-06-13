from django.db import models
from django.contrib.auth.models import User

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

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='delivery_crew', null=True)
    date = models.DateField()
    status = models.CharField(
        max_length=10,
        choices = StatusChoices.choices,
        default= StatusChoices.PENDING
    )

    

class OrderItem(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    @property
    def item_subtotal(self):
        return self.menu_item.price * self.quantity
    
    def __str__(self):
        return f"{self.quantity} x {self.menu_item.price} in order {self.order.pk}"
    
    class Meta():
        unique_together = ('menu_item', 'order')

    
