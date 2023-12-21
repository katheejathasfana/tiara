from django.db import models
from authentication.models import *
from adminapp.models import *

class Cart(models.Model):
    user = models.OneToOneField(Custom_user, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)

class CartItem(models.Model): 
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class Address(models.Model):
    user=models.ForeignKey(Custom_user, on_delete=models.CASCADE, related_name='addresses')
    full_name=models.CharField(max_length=50, null=True, blank=True)
    address=models.TextField(null=True, blank=True)
    city=models.CharField(max_length=50,null=True, blank=True)
    country=models.CharField(max_length=50, null=True, blank=True)
    pincode=models.IntegerField(null=True, blank=True)
    phone_No=models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.full_name
    

class Order(models.Model):
    user = models.ForeignKey(Custom_user, on_delete=models.CASCADE, related_name='orders')
    address=models.ForeignKey(Address, on_delete=models.CASCADE, related_name='orders')
    products= models.ManyToManyField(Product,through='OrderItem')
    # price=models.DecimalField(default=0,max_digits=10, decimal_places=2)
    is_paid=models.BooleanField(default=False)
    order_date=models.DateField(auto_now=True)
    payment_method = models.CharField(max_length=50, default='Cash On Delivery')
    total_amount=models.DecimalField(max_digits=10,decimal_places=2)
    shipping_charge=models.DecimalField(default=10, max_digits=10,decimal_places=2)
    Grand_total=models.DecimalField(default=0, max_digits=10,decimal_places=2)

    ORDER_STATUS_CHOICES = [
       
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('cancelled', 'Cancelled'),
        ('delivered', 'Delivered'),
    ]
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='confirmed')
    def __str__(self):
        return f"Order {self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"