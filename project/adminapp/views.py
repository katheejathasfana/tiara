import datetime
from os import truncate
import os
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.shortcuts import get_object_or_404, render,redirect
from authentication.models import *
from project import settings
from userdetails.models import Wallet,  WalletTransaction
from .models import *
from cart.models import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control,never_cache
from django.db.models import Sum,Count
from datetime import datetime
from django.contrib.admin.views.decorators import staff_member_required


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

@staff_member_required(login_url='admin_login')
@login_required(login_url='admin_login')
def dashboard(request):
    user=Custom_user.objects.count()
    total_orders=Order.objects.count()
    pending_orders=Order.objects.filter(status="confirmed").count()
    shipping_orders=Order.objects.filter(status="shipping").count()
    total_revenue = Order.objects.filter(payment_status='1').aggregate(
    total_amount_sum=Sum('total_amount'))['total_amount_sum']
    order_data = Order.objects.values('order_date').annotate(total_amount=Sum('Grand_total'))
    orders = Order.objects.all()

    orders_by_month = {}
    orders_by_year = {}
    orders_by_day = {}
    chart_labels=None
    chart_data=None

    for o in orders:
        month = o.order_date.month
        if month in orders_by_month:
            orders_by_month[month] += o.quantity
        else:
            orders_by_month[month] = o.quantity

        year = o.order_date.year
        if year in orders_by_year:
            orders_by_year[year] += o.quantity
        else:
            orders_by_year[year] = o.quantity

        day = o.order_date.day
        if day in orders_by_day:
            orders_by_day[day] += o.quantity
        else:
            orders_by_day[day] = o.quantity

    detailed_report = None

    if request.method == 'POST':
        report = request.POST.get('status')

        if report == 'yearly':
            chart_labels = list(orders_by_year.keys())
            chart_data = list(orders_by_year.values())
            detailed_report = Order.objects.filter(order_date__year=datetime.now().year)

        elif report == 'monthly':
            chart_labels = list(orders_by_month.keys())
            chart_data = list(orders_by_month.values())
            detailed_report = Order.objects.filter(order_date__month=datetime.now().month)

        elif report == 'daily':
            chart_labels = list(orders_by_day.keys())
            chart_data = list(orders_by_day.values())
            detailed_report = Order.objects.filter(order_date=datetime.now().date())
   
    context = {
        'user': user,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'shipping_order':shipping_orders,
        'total_revenue': total_revenue,
        'order_data': order_data,
        'chart_labels': chart_labels,
        'chart_data':chart_data,
        'detailed_report':detailed_report
        
     }
    return render(request,'admin/dashboard.html',context)


@staff_member_required(login_url='admin_login')
def sales_report(request):
    # Fetch sales data, grouping by order date
    sales_data = Order.objects.values('order_date').annotate(
        total_sales=Sum('total_amount'),
        total_items=Sum('quantity'),
        total_orders=Count('id'),
    )

    # Calculate overall statistics
    total_orders = Order.objects.count()
    total_amount = Order.objects.aggregate(Sum('total_amount'))['total_amount__sum']
    average_order_value = total_amount / total_orders if total_orders > 0 else 0

    context = {
        'sales_data': sales_data,
        'total_orders': total_orders,
        'total_amount': total_amount,
        'average_order_value': average_order_value,
    }

    return render(request, 'admin/sales_report.html', context)

@staff_member_required(login_url='admin_login')
def signout(request):
    logout(request)
    return redirect('admin')


@staff_member_required(login_url='admin_login')
@login_required(login_url='admin_login')
def users(request):
    users=Custom_user.objects.all().exclude(is_superuser=True)
    return render(request,'admin/users.html',{'users':users})

@staff_member_required(login_url='admin_login')
@login_required(login_url='admin_login')
def user_active(request,id):
    if request.method=='POST':
        user=Custom_user.objects.get(id=id)
        if not user.is_superuser:
            user.is_active= not user.is_active
            user.save()
            return  redirect('users')
        return redirect('users')


@staff_member_required(login_url='admin_login')   
@login_required(login_url='admin_login')
def get_user(request,id):
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

# def delete_user(request,id):
#     user=Custom_user.objects.get(id=id)
#     user.delete()
#     return redirect('users')

@staff_member_required(login_url='admin_login')
@login_required(login_url='admin_login')
def category(request):
    categories=Category.objects.all()
    return render(request,'admin/category.html',{'categories':categories})

@staff_member_required(login_url='admin_login')
@login_required(login_url='admin_login')
def category_active(request,id):
    if request.method=='POST':
        categry=Category.objects.get(id=id)
        categry.active= not categry.active
        categry.save()
        img2=request.FILES.get("img2")
        
    return redirect('category')

@staff_member_required(login_url='admin_login')
@login_required(login_url='admin_login')
def add_category(request):
    if request.method == "POST":
        category_name = request.POST.get("name")
        offer = request.POST.get("offer")
        expire = request.POST.get("expire")
        image = request.FILES.get("image")

        if not category_name or category_name.isspace():
            messages.error(request, 'Please enter a valid category name')
            return redirect('category')

        if Category.objects.filter(name__iexact=category_name).exists():
            messages.error(request, 'Category already exists')
            return redirect('category')
        
        if offer and expire:
            if not 0 <= int(offer) <= 100:
                messages.error(request, 'Please enter a valid discount percentage ')
                return redirect('category')
            
            offer = CategoryOffer(discount_prcnt=offer, expire_date=expire)
            offer.save()
        

        elif offer and not expire:
            messages.error(request, 'Please enter an expiration date')
            return redirect('category')

        else:
            offer = None
       
        category = Category(name=category_name, offer=offer)
        if not image:
            messages.error(request, 'Please upload an image for the category')
            return redirect('category')
           
        elif image.content_type.startswith('image'):
            category.image = image
            category.save()
            messages.success(request, 'Category added successfully')
        else:
            messages.error(request, 'Please upload a valid image file')
        return redirect('category')

@staff_member_required(login_url='admin_login')  
@login_required(login_url='admin_login')
def get_category(request,id):
    category=Category.objects.get(id=id)
    return render(request,'admin/update_category.html',{'category':category})

@staff_member_required(login_url='admin_login')
@login_required(login_url='admin_login')
def update_category(request, id):
    category = get_object_or_404(Category, id=id)
    category.name = request.POST.get('name')
    offer = request.POST.get("offer")
    expire = request.POST.get("expire")
    if 'image' in request.FILES:
        category.image = request.FILES['image']
    image = request.FILES.get("image")

    if not category.name or not category.image or category.name.isspace():
        messages.error(request, 'FIll the required fields')
        return redirect('get_category',id=id)
    if Category.objects.exclude(id=id).filter(name__iexact=category.name).exists():
        messages.error(request, 'Category with this name already exists')
        return redirect('get_category',id=id)
    if offer and expire:
        try:
            offer = int(offer)
            if not 0 <= offer <= 100:
                messages.error(request, 'Please enter a valid discount percentage')
                return redirect('get_category',id=id)
        except ValueError:
            messages.error(request, 'Please enter a valid numeric value for the discount percentage')
            return redirect('get_category',id=id)
       
        category_offer, created = CategoryOffer.objects.get_or_create(
            defaults={'discount_prcnt': offer},
            expire_date=expire
        )
        category.offer = category_offer

    elif offer and not expire:
        messages.error(request, 'Please enter an expiration date')
        return redirect('get_category', id=id)

    else:
        category.offer = None

    if image:
        if image.content_type.startswith('image'):
            category.image = image
            category.save()
        else:
            messages.error(request, 'Please upload a valid image file')
            return redirect('get_category', id=id)
    
    remove_image = request.POST.get("remove_image")

    if remove_image and category.image:
   
        old_image_path = os.path.join(settings.MEDIA_ROOT, str(category.image))
        if os.path.exists(old_image_path):
            os.remove(old_image_path)
        category.image = None


    category.save()
    messages.success(request, 'Category updated successfully')
    return redirect('category')



@staff_member_required(login_url='admin_login')
@login_required(login_url='admin_login')
def delete_category(request,id):
    category=Category.objects.get(id=id)
    category.delete()
    return redirect('category')

@staff_member_required(login_url='admin_login')
@login_required(login_url='admin_login')
def product(request):
    products=Product.objects.all()
    variants=Variant.objects.all()
    category=Category.objects.all()
    return render(request,'admin/product.html',{'products':products , 'categories':category, 'variants':variants} )

@staff_member_required(login_url='admin_login')
@login_required(login_url='admin_login')
def product_active(request,id):
    if request.method=='POST':
        product=Product.objects.get(id=id)
        product.active= not product.active
        product.save()
        
    return redirect('product')


@staff_member_required(login_url='admin_login')
@login_required(login_url='admin_login')
def add_product(request):
    if request.method == 'POST':
        name = request.POST.get("name")
        product_offer = None
        offer = request.POST.get("offer")
        expire = request.POST.get("expire")

        if not name  or name.isspace():
            messages.error(request, "Please fill in all required fields")
            return redirect('product')
        
        if Product.objects.filter(productname=name).exists():
            messages.error(request, "product already exists")
            return redirect('product')
        
        if offer and expire:
            if not 0 <= int(offer) <= 100:
                messages.error(request, 'Please enter a valid discount percentage ')
                return redirect('product')
            
            product_offer = ProductOffer(discount_prcnt=offer, expire_date=expire)
            product_offer.save()
       
        category = request.POST.get("category")
        details = request.POST.get("product_details")
        description = request.POST.get("description")
        
    product = Product.objects.create(
            productname=name,
            category_id=category,
            details=details,
            description=description,
            active=True,
            offer=product_offer,
        )

    product.save()

    if product_offer is not None:
        product_offer.save()
    return redirect('product')

@staff_member_required(login_url='admin_login')
@login_required(login_url='admin_login')
def get_product(request,id):
    product=Product.objects.get(id=id)
    category=Category.objects.all()
    return render(request,'admin/update_product.html',{'product':product , 'categories':category} )

@staff_member_required(login_url='admin_login')
@login_required(login_url='admin_login')
def update_product(request, id):
    product = Product.objects.get(id=id)
    product.productname = request.POST.get('name')
    product.category_id = request.POST.get('category')
    product.description = request.POST.get('description')

    if not product.productname or product.productname.isspace():
        messages.error(request, "Please fill in all required fields")
        return redirect('get_product', id=id)

    offer = request.POST.get("offer")
    expire = request.POST.get("expire")

    # Check if both offer and expire are provided
    if offer and expire:
        try:
            offer_percentage = int(offer)
            if not 0 <= offer_percentage <= 100:
                raise ValueError("Please enter a valid discount percentage between 0 and 100")
            
            # Check if the product already has an offer
            if product.offer:
                product.offer.discount_prcnt = offer_percentage
                product.offer.expire_date = datetime.strptime(expire, '%Y-%m-%d')
                product.offer.save()
            else:
                # Create a new offer if none exists
                product_offer = ProductOffer.objects.create(
                    discount_prcnt=offer_percentage,
                    expire_date=datetime.strptime(expire, '%Y-%m-%d')
                )
                product.offer = product_offer
        except ValueError as e:
            messages.error(request, f'Invalid offer percentage: {e}')
            return redirect('get_product', id=id)
    else:
        # If offer or expire is missing, check if product has an existing offer and set it to None
        if product.offer:
            product.offer = None

    product.save()

    return redirect('product')

@staff_member_required(login_url='admin_login')
@login_required(login_url='admin_login')
def variant(request, id):
    product = get_object_or_404(Product, id=id)
    request.session['id']=id
    variants = Variant.objects.filter(product=product)
    return render(request,'admin/variant.html',{'variants': variants})

@staff_member_required(login_url='admin_login')
@login_required(login_url='admin_login')
def add_variant(request):
    id = request.session.get('id')
    product = Product.objects.get(id=id)       
    if request.method == 'POST':
        color = request.POST.get("color")
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        img1 = request.FILES.get("img1")
        img2 = request.FILES.get("img2")
        img3 = request.FILES.get("img3")
        img4 = request.FILES.get("img4")

        if not color or not price or not stock or not img1 or color.isspace():
            messages.error(request, "Fill in all mandatory fields")
            return redirect('variant', id)
        
        try:
            
            price = float(price)
            stock = float(stock)
            
            if price <= 0 or stock < 0:
                messages.error(request, "Please enter valid numbers for price and stock.")
                return redirect('variant', id)
        except ValueError:
            # Handle the case where price or stock is not a valid integer
            messages.error(request, "Please enter valid numbers for price and stock.")
            return redirect('variant', id)

        variant = Variant.objects.create(
            product=product,
            color=color,
            price=price,
            stock=stock,
            img1=img1,
            img2=img2,
            img3=img3,
            img4=img4
        )
        return redirect('variant', id=id)

@staff_member_required(login_url='admin_login')
@login_required(login_url='admin_login')
def get_variant(request,id):
    variant=Variant.objects.get(id=id)
    return render(request,'admin/update_variant.html',{'variant':variant } )

    
@staff_member_required(login_url='admin_login')
@login_required(login_url='admin_login')
def update_variant(request, id):
    variant = Variant.objects.get(id=id)   
    product=variant.product
    variant.color = request.POST.get('color')
    variant.price = request.POST.get('price')
    variant.stock = request.POST.get('stock')
    if 'img1' in request.FILES:
        variant.img1 = request.FILES['img1']
    if 'img2' in request.FILES:
        variant.img2 = request.FILES['img2']
    if 'img3' in request.FILES:
        variant.img3 = request.FILES['img3']
    if 'img4' in request.FILES:
        variant.img4 = request.FILES['img4']

    if not variant.color or not variant.price or not variant.stock or not variant.img1 or variant.color.isspace():
        messages.error(request, "Fill in all mandatory fields")
        return redirect('get_variant', id)
    
    if float(variant.price) <= 0 or float(variant.stock)< 0:
        messages.error(request, "Please enter valid numbers for price and stock.")
        return redirect('get_variant', id=id)
    
    remove_image = request.POST.getlist("remove_image")
    for image in remove_image:
        if image == "img1":
            variant.img1 = None
        elif image == "img2":
            variant.img2 = None
        elif image == "img3":
            variant.img3 = None
        elif image == "img4":
            variant.img4 = None


    variant.save()
    return redirect('variant',product.id)

@staff_member_required(login_url='admin_login')
@login_required(login_url='admin_login')
def delete_variant(request,id):
    try:
        varient=Variant.objects.get(id=id)
        varient.delete()
    except:
        pass
    return redirect('variant',id=id)

    
@staff_member_required(login_url='admin_login')
@login_required(login_url='admin_login')
def delete_product(request,id):
    try:
        product=Product.objects.get(id=id)
        product.delete()
    except:
        pass
    return redirect('product')

@staff_member_required(login_url='admin_login')
@login_required(login_url='admin_login')
def order(request):
    orders=Order.objects.all().order_by('-id')
    return render(request ,'admin/order.html',{'orders': orders})

@staff_member_required(login_url='admin_login')    
@login_required(login_url='admin_login')
def order_view(request,id):
    transaction= request.GET.get('transaction_id')
    print(transaction)
    order=Order.objects.get(id=id)
    return render(request, 'admin/order_view.html', {'order':order, 'transaction':transaction})

@staff_member_required(login_url='admin_login')   
@login_required(login_url='admin_login')
def change_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('new_status')
        order.status = new_status
        if order.status=='cancelled':
            order.save()
        if order.payment_method=='Online payment' or 'Wallet':
            refund_amount=order.Grand_total
            user=order.user
            wallet, created = Wallet.objects.get_or_create(user=user)
            wallet.balance+=refund_amount
            WalletTransaction.objects.create(user=request.user, amount=refund_amount, transaction_type='credit', transaction_details= "Tiara"+ str(order.id) + " order cancelled")

            
            wallet.save()
        return redirect('order') 
    return render(request, 'admin/order.html', {'order': order})

@staff_member_required(login_url='admin_login')
@login_required(login_url='admin_login')
def coupons(request):
    coupons=Coupon.objects.all()
    return render(request,'admin/coupon.html',{'coupons':coupons})


@login_required(login_url='admin_login')
def add_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        percentage = request.POST.get('percentage')
        min_amount = request.POST.get('min')
        try:
            if Coupon.objects.filter(code=code).exists():
                messages.error(request,"coupon alreaddy exists")
                return redirect('coupons')
        except:
            pass
        if not code or not percentage or not min_amount or code.isspace():
            messages.error(request, "Fill in all the required fields")
            return redirect('coupons')
    
        min_amount = float(min_amount)
        percentage = float(percentage)

        if min_amount < 0 or percentage < 0 or percentage > 100:
            messages.error(request, "Invalid values for minimum amount or percentage")
            return redirect('coupons')

        coupon = Coupon.objects.create(code=code, dis_per=percentage, minimum_amount=min_amount).save()
        messages.success(request, "Coupon added successfully")
    return redirect('coupons')

        
    

@login_required(login_url='admin_login')
def coupon_active(request,id):
    if request.method=='POST':
        coupon=Coupon.objects.get(id=id)
        coupon.active= not coupon.active
        coupon.save() 
    return redirect('coupons')

