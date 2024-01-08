from django.shortcuts import render,redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.utils import timezone
from project.settings import EMAIL_HOST_USER
from .models import *
from random import randint
from django.core.mail import send_mail
from django.conf import settings
from adminapp.models import *
from django.shortcuts import render, get_object_or_404
from cart.models import *

from userdetails.models import Wishlist, Wallet

def home(request):
    categories=Category.objects.all()
    cartitem=CartItem.objects.count()
    wishlist=Wishlist.objects.count()
    print(wishlist)
    return render(request,'user/Home.html',{'categories': categories, 'wishlist':wishlist, 'cartitem':cartitem})

def signin(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email= request.POST.get('email')
        password = request.POST.get('password')
        try:
            if email=="":
                messages.error(request,'email not be blank')
                return render(request,'user/login.html')
            
            user = Custom_user.objects.get(email=email)
            user = authenticate(request, email=email, password=password)
            

            if user is not None and user.is_verified==True and user.is_active==True:
                login(request, user)
            
            else:
                messages.error(request,'Incorrect Username or Password')
            
            return redirect('login')
            
        
        except Custom_user.DoesNotExist:
            messages.error(request, 'Email not registered')
    return render(request,'user/login.html')

def signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmpassword')

        if not name or not email or not password or not confirm_password:
            messages.error(request, "Please fill in all required fields")
            return redirect('signup')
        
        if Custom_user.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered')
            return render(request, 'user/signup.html')
        
        if not is_strong_password(password):
            messages.error(request,'password should be strong')
            return render(request, 'user/signup.html')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'user/signup.html')
        
        

        otp = randint(100000, 999999)
        print(otp)
        send_mail("One Time Password (OTP) for Registration", f" otp:{otp} OTP for account verification ", EMAIL_HOST_USER, [email], fail_silently=True)

        user = Custom_user.objects.create(email=email, name=name,otp=otp)
        
        user.set_password(password)
        user.save()
        Wallet.objects.create(user=user, balance=0)

       
        return redirect('verification', email=email)

    return render(request, 'user/signup.html')

def is_strong_password(password):
    if len(password)<8:
        return False
    if not any(char.isupper()for char in password):
        return False
    if not any(char.islower()for char in password):
        return False
    if not any (char.isdigit() for char in password):
        return False
    special_char="!@#$%^&*(){}[]:;,.'<>"
    if not any(char in special_char for char in password):
        return False
    return True


def resend_otp(request,email):
    user=Custom_user.objects.get(email=email)
    # if user.otp_created_at+user.otp_exioriy<timezone.now():
    new_otp=randint(100000,999999)
    user.otp=new_otp
    user.save()
    print(new_otp)

    user.otp=new_otp
    user.otp_created_at=timezone.now()
    user.save()
    send_mail("One Time Password (OTP) for Registration", f" otp:{new_otp} OTP for account verification ",
                    EMAIL_HOST_USER, [email], fail_silently=True)
    messages.success(request,'OTP sent succesfully')
    return redirect('verification',email=email)
    


def verification(request, email):
    print(email)
    if request.method == 'POST':
        otp_entered = "".join(request.POST.get(f'otp{i}', '') for i in range(1, 7))
        print(otp_entered)
        print(type(otp_entered))
        user=Custom_user.objects.get(email=email)
        print(type(user.otp))
        print(user.otp)
        if user:
            if otp_entered==str(user.otp):
                user.is_verified=True
                user.save()
                messages.success(request,"Account created succesfully")
                return redirect('login')
            else:
                messages.error(request,"Otp is Inccorect")
            
                return render(request,'user/verification.html',{'email':email})
            
    return render(request,'user/verification.html',{'email':email})




def forgetpassword(request):
    if request.method=='POST':
        email=request.POST.get("email")
        print(email)
        user=Custom_user.objects.filter(email=email).first()
        print(user)
        if user:
            otp=randint(100000,999999)
            user.otp=otp
            user.save()
            print(otp)
            send_mail("One Time Password (OTP) for Registration",f" otp:{otp} OTP for account verification ",EMAIL_HOST_USER,[email],fail_silently=True)
            return redirect('otp_verify',email=email)
        else:
            messages.error(request,"User deosn't exist")
            return redirect('login')
        
def otp_verify(request, email):
    if request.method == 'POST':
        otp_entered = "".join(request.POST.get(f'otp{i}', '') for i in range(1, 7))
        user = Custom_user.objects.get(email=email)

        if user:
            if otp_entered == str(user.otp):
                user.is_verified = True
                user.save()
                messages.success(request, "Password reset successfully")
                return redirect('resetpassword', email=user.email)
            else:
                messages.error(request, "Otp is incorrect")
                return render(request, 'user/otp_verify.html', {'email': email})

    return render(request, 'user/otp_verify.html', {'email': email})

def resetpassword(request,email):

    user=Custom_user.objects.get(email=email)
    if user.is_verified:
        if request.method=="POST":
            password=request.POST.get('password')
            confirm_password=request.POST.get("confirmpassword")
            if password != confirm_password:
                messages.error(request, 'Passwords do not match')
                return redirect('resetpassword',email=email)
            user.set_password(password)
            user.save()
            return redirect('login')
        return render(request, 'user/resetpassword.html', {'email':email})
    
        
            


def signout(request):
    logout(request)
    return redirect('login')


def products(request):
    products=Product.objects.all()
    
    order_by = request.GET.get('order_by', 'default')
    if order_by == 'low_to_high':
        products = products.order_by('price')
    elif order_by == 'high_to_low':
        products = products.order_by('-price')
    return render(request,'user/products.html',{'products':products})

def product_details(request,id):
    product=Product.objects.get(id=id)
    variants=Varient_color.objects.all()
    request.session['product_id'] = product.id
    return render(request,'user/productdetails.html',{'product':product , 'variants':variants})

def category_product(request, id):
    categories = Category.objects.get(id=id)
    products = Product.objects.filter(category=categories, active=True)
    return render(request, 'user/categories.html', {'categories': categories, 'products': products})


def search(request):
    if request.POST.get('search'):
        search=request.POST.get('search')
        if search:
       
            products = Product.objects.filter(productname__icontains=search)

            return render(request, 'user/products.html', {'products': products})
    return redirect('home')
