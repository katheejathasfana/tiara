from django.db import models

class Category(models.Model):
    name=models.CharField(max_length=50)
    Category_id=models.IntegerField(primary_key=True)


class Product(models.Model):
    Category_id=models.ForeignKey(Category,on_delete=models.CASCADE)
    name=models.CharField(max_length=20)
    

# Create your models here.
