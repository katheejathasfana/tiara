from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.shortcuts import get_object_or_404, render,redirect
from authentication.models import *
from .models import *
from cart.models import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control,never_cache

@never_cache
def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username,password)
        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('dashboard')

        else:
            messages.error(request, 'Invalid credentials for admin login')
    
    return render(request, 'admin/admin.html')


@login_required(login_url='admin_login')
def dashboard(request):
    return render(request,'admin/dashboard.html')

def signout(request):
    logout(request)
    return redirect('admin')
@login_required(login_url='admin_login')
def users(request):
    users=Custom_user.objects.all().exclude(is_superuser=True)
    return render(request,'admin/users.html',{'users':users})

@login_required(login_url='admin_login')
def user_active(request,id):
    if request.method=='POST':
        user=Custom_user.objects.get(id=id)
        if not user.is_superuser:
            user.is_active= not user.is_active
            user.save()
            return  redirect('users')
        return redirect('users')
@login_required(login_url='admin_login')
def get_user(
    
    request,id):
    user=Custom_user.objects.get(id=id)
    return render(request, 'update.html',{'users':user}) 

# def update_user(request,id):
#     user=Custom_user.objects.get(id=id)
#     user.name=request.POST['name']
#     user.email=request.POST['email']
#     if user.name==" ":
#         messages.error(request,'cant update')
#         return render(request,'update.html')
#     else:
#         user.save()
#     return redirect('users')

def delete_user(request,id):
    user=Custom_user.objects.get(id=id)
    user.delete()
    return redirect('users')


@login_required(login_url='admin_login')
def category(request):
    categories=Category.objects.all()
    return render(request,'admin/category.html',{'categories':categories})


def category_active(request,id):
    if request.method=='POST':
        categry=Category.objects.get(id=id)
        categry.active= not categry.active
        categry.save()
        img2=request.FILES.get("img2")
        
    return redirect('category')

def add_category(request):
    if request.method == "POST": 
        category_name = request.POST.get("name")
        if Category.objects.filter(name=category_name).exists():
            messages.error(request,'category already exist')
            return redirect('category')

        image=request.FILES.get("image")
        if Category.objects.filter(name=category_name).exists():
            messages.error(request, "category already exists")
            return redirect('category')
        

        category=Category.objects.create(name=category_name,image=image)
        print(category)
        category.save()
        return redirect('category')
    else:
        return redirect('category')

def delete_category(request,id):
    category=Category.objects.get(id=id)
    category.delete()
    return redirect('category')

@login_required(login_url='admin_login')
def product(request):
    products=Product.objects.all()
    variants=Varient_color.objects.all()
    category=Category.objects.all()
    return render(request,'admin/product.html',{'products':products , 'categories':category, 'variants':variants} )

def product_active(request,id):
    if request.method=='POST':
        product=Product.objects.get(id=id)
        product.active= not product.active
        product.save()
        
    return redirect('product')

@login_required(login_url='admin_login')
def add_product(request):
    stock=0
    price=0
    if request.method=='POST':
        name=request.POST.get("name")
        category=request.POST.get("category")
        price=request.POST.get("price")
        stock=request.POST.get("stock")
        details=request.POST.get("product_details")
        img1=request.FILES.get("img1")
        img2=request.FILES.get("img2")
        img3=request.FILES.get("img3")
        img4=request.FILES.get("img4")
        description=request.POST.get("description")
        variant = request.POST.get('variant')
   

        if not name or not price or not category or not stock or not img1:
            messages.error(request, "Please fill in all required fields")
            return
           
        
    stock = int(stock) if stock is not None else None
    price = float(price) if price is not None else None
    if price <= 0 or stock < 0:
        messages.error(request, "Please enter valid numbers for price and stock.")
        return redirect('add_product')

    product=Product.objects.create(productname=name,category_id=category,price=price,stock=stock,details=details,img1=img1,img2=img2,img3=img3,img4=img4,description=description, varient_id=variant)
    product.save()
    return redirect('product')
    


def get_product(request,id):
    product=Product.objects.get(id=id)
    category=Category.objects.all()
    return render(request,'admin/update_product.html',{'product':product , 'categories':category} )

    
@login_required(login_url='admin_login')
def update_product(request, id):
    product = Product.objects.get(id=id)

    
    product.productname = request.POST.get('name')
    product.category_id = request.POST.get('category')
    product.price = request.POST.get('price')
    product.stock = request.POST.get('stock')
    product.description = request.POST.get('description')
   

    if 'img1' in request.FILES:
        product.img1 = request.FILES['img1']
    if 'img2' in request.FILES:
        product.img2 = request.FILES['img2']
    if 'img3' in request.FILES:
        product.img3 = request.FILES['img3']
    if 'img4' in request.FILES:
        product.img4 = request.FILES['img4']

    if not product.productname or not product.price or not product.category_id or not product.stock or not product.img1:
        messages.error(request, "Please fill in all required fields")
        return redirect('get_product', id=id)
        
    stock = int(product.stock) if product.stock is not None else None
    print(type(stock))
    price = float(product.price) if product.price is not None else None
    if price <= 0 or stock < 0:
        messages.error(request, "Please enter valid numbers for price and stock.")
        return redirect('get_product', id=id)

    product.save()
    return redirect('product')


@login_required(login_url='admin_login')
def delete_product(request,id):
    product=Product.objects.get(id=id)
    product.delete()
    return redirect('product')

@login_required(login_url='admin_login')
def order(request):
    orders=Order.objects.all()
    
    return render(request ,'admin/order.html',{'orders': orders})
@login_required(login_url='admin_login')
def order_view(request,id):
    transaction= request.GET.get('transaction_id')
    print(transaction)
    order=Order.objects.get(id=id)
    return render(request, 'admin/order_view.html', {'order':order, 'transaction':transaction})
    
@login_required(login_url='admin_login')
def change_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('new_status')
        order.status = new_status
        order.save()
        return redirect('orders') 
    return render(request, 'admin/order.html', {'order': order})

def variant(request):
    variants=Varient_color.objects.all()
    return render(request,'admin/variant.html',{'variants': variants})

def add_variant(request):
    if request.method=='POST':
        name=request.POST.get("name")
        Varient_color.objects.create(name=name).save()
        return redirect('variant')

def delete_variant(request,id):
    varient=Varient_color.objects.get(id=id)
    varient.delete()
    return redirect('variant')


def coupons(request):
    coupons=Coupon.objects.all()
    return render(request,'admin/coupon.html',{'coupons':coupons})

def add_coupon(request):
    if request.method=='POST':
        
        code=request.POST.get('code')
        price=request.POST.get('price')
        min_amount=request.POST.get('min')
        coupon=Coupon.objects.create(code=code, dis_per=price,minimum_amount=min_amount)
        return redirect('coupons')
    
def delete_coupon(request,id):
    coupon=Coupon.objects.get(id=id)
    coupon.delete()
    return redirect('coupons')