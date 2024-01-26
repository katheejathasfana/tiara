
from datetime import date
from django.db import models
from authentication.models import *
from django.core.validators import MinValueValidator, MaxValueValidator

class ProductOffer(models.Model):
    discount_prcnt = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    expire_date = models.DateField()

class CategoryOffer(models.Model):
    discount_prcnt = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    expire_date = models.DateField()
    
class Category(models.Model):
    name=models.CharField(max_length=50)
    active=models.BooleanField(default=True)
    image=models.ImageField(upload_to='category_images',blank=True)
    offer=models.ForeignKey(CategoryOffer, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.name
    
class Product(models.Model):
    productname=models.CharField(max_length=50)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    details=models.CharField(max_length=100, default='None')
    description=models.TextField()
    active = models.BooleanField(null=True, blank=True)
    offer = models.ForeignKey(ProductOffer, on_delete=models.SET_NULL, null=True, blank=True) 

    def __str__(self):
        return self.productname
   
    
class Variant(models.Model):
    color=models.CharField(max_length=50, default="None")
    product=models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    price = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    stock=models.IntegerField(default=0)
    img1=models.ImageField(upload_to='product_images',blank=True)
    img2=models.ImageField(upload_to='product_images',blank=True)
    img3=models.ImageField(upload_to='product_images',blank=True)
    img4=models.ImageField(upload_to='product_images',blank=True)
    active=models.BooleanField(default=True)
    discount_price = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    
    def save(self, *args, **kwargs):
        if self.product:
            product_offer = self.product.offer
            if product_offer and product_offer.expire_date >= date.today():
                self.discount_price = round(float(self.price) - (float(self.price) * product_offer.discount_prcnt / 100))
            else:
                self.discount_price = self.price
        elif self.product.category:
            category_offer = self.product.category.offer
            if category_offer and category_offer.expire_date >= date.today():
                self.discount_price = round(float(self.price) - (float(self.price) * category_offer.discount_prcnt / 100))
            else:
                self.discount_price = self.price

        super().save(*args, **kwargs)

class Coupon(models.Model):
    code=models.CharField(max_length=10, unique=True)
    dis_per=models.IntegerField()
    minimum_amount=models.PositiveBigIntegerField(default=0)
    active=models.BooleanField(default=True)
    



