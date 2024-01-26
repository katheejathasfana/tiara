from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Custom_user

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = Custom_user
        fields = ('email', 'password1', 'password2', 'name', 'date_of_birth', 'phone_Number', 'address', 'gender', 'pro_pic', 'referal_code')