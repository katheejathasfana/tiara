from django.db import models
from authentication.models import *
from adminapp.models import *
from decimal import Decimal
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver



class Cart(models.Model):
    user = models.OneToOneField(Custom_user, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    total=models.DecimalField(max_digits=10,decimal_places=2, default=0)
    discnt=models.DecimalField(max_digits=10,decimal_places=2, default=0)
    total_quantity=models.IntegerField(default=0)
    shipping_charge=models.DecimalField(default=40, decimal_places=2, max_digits=10)
    grand_total=models.DecimalField(max_digits=10,decimal_places=2, default=0)

    def summarycart(self):
        cartitems = self.cartitem_set.all() 
        total = sum(Decimal(item.product.price) * item.quantity for item in cartitems)
        total_quantity = sum(item.quantity for item in cartitems)
        Grand_total = total + Decimal(self.shipping_charge)-Decimal(self.discnt)
        self.total = total
        self.grand_total = Grand_total
        self.total_quantity = total_quantity
        self.save()
# @receiver(pre_delete, sender=CartItem)
# @receiver(post_save, sender=CartItem)
# def update_cart_on_cartitem_change(sender, instance, **kwargs):
#     instance.cart.update_discount()

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
    address=models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    products= models.ManyToManyField(Product,through='OrderItem')
    order_date=models.DateField(auto_now=True)
    total_amount=models.DecimalField(max_digits=10,decimal_places=2)
    shipping_charge=models.DecimalField(default=40, max_digits=10,decimal_places=2)
    discount=models.DecimalField(default=0, max_digits=10,decimal_places=2)
    Grand_total=models.DecimalField(default=0, max_digits=10,decimal_places=2)
    
    payment_status_choices=[(1,'Completed'),
                            (2, 'Failure'),
                            (3,'Pending'),
                            ]
    payment_status=models.IntegerField(choices=payment_status_choices, default=3)
    
    ORDER_STATUS_CHOICES = [   
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('cancelled', 'Cancelled'),
        ('delivered', 'Delivered'),
    ]
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='confirmed')

    payment_method_choices=[
        ('COD','Cash On Delivery'),
        ('Online Payment','Online Payment'),
    ]
    payment_method = models.CharField(max_length=50,default=None)

    
    
    
    def __str__(self):
        return f"Order {self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    quantity = models.PositiveIntegerField(default=1)
    product_price=models.DecimalField(default=0, max_digits=10,decimal_places=2)
    def __str__(self):
        return f"{self.product.name} - {self.quantity}"