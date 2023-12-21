
from django.db import models

class Category(models.Model):
    name=models.CharField(max_length=50)
    active=models.BooleanField(default=True)
    image=models.ImageField(upload_to='category_images',blank=True)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    productname=models.CharField(max_length=50)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    price = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    stock=models.IntegerField(default=0)
    details=models.CharField(max_length=100, default='None')
    description=models.TextField()
    img1=models.ImageField(upload_to='product_images',blank=True)
    img2=models.ImageField(upload_to='product_images',blank=True)
    img3=models.ImageField(upload_to='product_images',blank=True)
    img4=models.ImageField(upload_to='product_images',blank=True)
    active=models.BooleanField(default=True)

    def __str__(self):
        return self.productname
    



