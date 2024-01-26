from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .manager import CustomUserManager

class Custom_user(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=50)
    otp = models.IntegerField(default=0000)
    otp_created_at = models.DateTimeField(auto_now=True)
    otp_expiry = models.DurationField(default=timezone.timedelta(minutes=1))
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_date = models.DateField(auto_now_add=True)
    name = models.CharField(max_length=50)
    date_of_birth = models.CharField(max_length=50)
    phone_Number = models.CharField(max_length=10)
    address = models.TextField()
    gender = models.CharField(max_length=10)
    is_staff = models.BooleanField(default=False)  
    pro_pic = models.ImageField(upload_to="User/image/User")
    referal_code = models.CharField(max_length=12, unique=True, blank=True, null=True)

    USERNAME_FIELD = 'email'

    objects = CustomUserManager()

    def __str__(self):
        return self.email

