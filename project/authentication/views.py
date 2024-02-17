from datetime import datetime, timedelta
from django.forms import ValidationError
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
from django.db.models import Min
import random
import string
from userdetails.models import *


def home(request):
    categories=Category.objects.all()
    return render(request,'user/Home.html',{'categories': categories})

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
                return redirect('home')
            
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
        request.session['email'] = email
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmpassword')
        referal_code = request.POST.get('referal_code')
        print(referal_code)

        if not name or not email or not password or not confirm_password:
            messages.error(request, "Please fill in all required fields")
            return redirect('signup')
        
        if Custom_user.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered')
            return render(request, 'user/signup.html')
        
        if not is_strong_password(password):
            messages.error(request,'password should be strong')
            return render(request, 'user/signup.html')
        
        if not email or '@' not in email:
            raise ValidationError('Please enter a valid email address.')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'user/signup.html')
        
        if referal_code is not None:
            request.session['referal_code'] = referal_code
            try:
                Custom_user.objects.get(referal_code=referal_code)
        
            except Custom_user.DoesNotExist:
               pass
           
        
        otp = randint(100000, 999999)
        otp_created_at = datetime.now()
        print(otp_created_at)
        
        # otp_created_at=timezone.make_aware(otp_created_at, timezone.get_default_timezone())
        user = Custom_user.objects.create(email=email, name=name,otp=otp, otp_created_at=otp_created_at)
        print(otp)
        print(timezone.localtime(user.otp_created_at))

        send_mail("One Time Password (OTP) for Registration", f" otp:{otp} OTP for account verification ", EMAIL_HOST_USER, [email], fail_silently=True)

        
       
        user.set_password(password)
        user.save()
        Wallet.objects.create(user=user, balance=0)       
        return redirect('verification')
    

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


def resend_otp(request):
    email=request.session.get('email')
    user=Custom_user.objects.get(email=email)
    new_otp=randint(100000,999999)
    user.otp_created_at = datetime.now()
    user.otp=new_otp
    user.save()
    print(new_otp)

    send_mail("One Time Password (OTP) for Registration", f" otp:{new_otp} OTP for account verification ",
                    EMAIL_HOST_USER, [email], fail_silently=True)
    messages.success(request,'OTP sent succesfully')
    return redirect('verification')
    


def verification(request):
    email = request.session.get('email')
    print(email)
    otp_time_limit = timedelta(minutes=1)
    current_time = datetime.now()
    print(current_time)
    current_time = timezone.make_aware(current_time, timezone.get_default_timezone())
    if request.method == 'POST':
        otp_entered = "".join(request.POST.get(f'otp{i}', '') for i in range(1, 7))
        signup_user = Custom_user.objects.get(email=email)  # Potential source of AttributeError
        referal_code = request.session.get('referal_code')
        if signup_user:  # Check if signup_user is not None
            if current_time - signup_user.otp_created_at <= otp_time_limit:  # Ensure signup_user is not None before accessing its attributes
                if otp_entered == str(signup_user.otp):
                    signup_user.is_verified = True
                    signup_user.referal_code = generate_referalcode()
                    signup_user.save()
                    if referal_code:
                        referal_bonus = 50
                        try:
                            provider = Custom_user.objects.get(referal_code=referal_code)
                            wallet = Wallet.objects.get(user=provider)
                            wallet.balance += referal_bonus
                            wallet.save()
                            WalletTransaction.objects.create(user=provider, amount=referal_bonus, transaction_type='credit', transaction_details="referal bonus")  
                            # user1 = authenticate(request, email=signup_user.email, password=signup_user.password)
                            # login(request, user1)
                            messages.success(request, "Account created successfully")
                            return redirect('login')
                        except:
                            # user1 = authenticate(request, email=signup_user.email, password=signup_user.password)
                            # login(request, user1)
                            return redirect('login')
                    else:
                        # user1 = authenticate(request, email=signup_user.email, password=signup_user.password)
                        # login(request, user1)
                        return redirect('login')                            
                
                else:
                    messages.error(request, "Otp is Incorrect")
                    return redirect('verification')
            else:
                signup_user.otp = 0
                signup_user.save()
                messages.error(request, "OTP expired")
                return redirect('verification')
    return render(request, 'user/verification.html')


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
    products=Product.objects.exclude(variants__isnull=True) 
    order_by = request.GET.get('order_by', 'default')
    if order_by == 'low_to_high':
        products = products.annotate(min_price=Min('variants__discount_price')).order_by('min_price')
    elif order_by == 'high_to_low':
        products = products.annotate(max_price=Min('discount_price')).order_by('-max_price')
    return render(request,'user/products.html',{'products':products})



def product_details(request,id):
    product = get_object_or_404(Product, id=id)
    variants = Variant.objects.filter(product=product)
    variant=variants.first()
    return render(request,'user/productdetails.html', {'variant':variant, 'variants':variants})

def category_product(request, id):
    categories = Category.objects.get(id=id)
    products = Product.objects.filter(category=categories, active=True)
    return render(request, 'user/products.html', {'categories': categories, 'products': products})

def product_detail(request,id):
    variant=Variant.objects.get(id=id)
    variants = Variant.objects.filter(product=variant.product)
    return render(request,'user/productdetails.html', {'variant':variant, 'variants':variants})


def search(request):
    if request.POST.get('search'):
        search=request.POST.get('search')
        if search:
            products = Product.objects.filter(productname__icontains=search)
            return render(request, 'user/products.html', {'products': products})
    return redirect('home')

def generate_referalcode():
    code_length=6
    code_character=string.ascii_uppercase+string.digits
    referral_code=''.join(random.choice(code_character)for _ in range(code_length))
    return referral_code