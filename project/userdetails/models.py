from django.db import models
from authentication.models import Custom_user
from adminapp.models import Product

# Create your models here.

class Wishlist(models.Model):
    user = models.ForeignKey(Custom_user, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class Wallet(models.Model):
    user=models.OneToOneField(Custom_user, on_delete=models.CASCADE)
    balance=models.DecimalField(default=0, max_digits=10,decimal_places=2)

class WalletTransaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=[('debit', 'Debit'), ('credit', 'Credit')])
    timestamp = models.DateTimeField(auto_now_add=True)