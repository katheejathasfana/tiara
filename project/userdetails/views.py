from urllib import response
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from cart.models import *
from django.db import transaction
from . models import *
from adminapp.models import *
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from datetime import datetime, date
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger




# Create your views here.
@login_required(login_url='login')
def profile(request):
    return render(request, 'user/profile_dtls.html')

@login_required(login_url='login')
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        user.name = request.POST.get('name', user.name)

        if not user.name or user.name.isspace():
            messages.error(request, "Enter a valid name")
            return redirect('edit_profile')

        user.phone_Number = request.POST.get('phone_Number', user.phone_Number)

        if not user.phone_Number.isdigit() or len(user.phone_Number) != 10:
            messages.error(request, "Enter a valid 10-digit phone number without spaces")
            return redirect('edit_profile')

        user.date_of_birth = request.POST.get('date_of_birth', user.date_of_birth)

        if user.date_of_birth:
            try:
                date_of_birth = datetime.strptime(user.date_of_birth, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Enter a valid date of birth in the format YYYY-MM-DD")
                return redirect('edit_profile')

            if date_of_birth >= date.today():
                messages.error(request, "Enter a valid date of birth")
                return redirect('edit_profile')

            user.date_of_birth = date_of_birth

        profile_image = request.FILES.get('profile_image')

        if profile_image and profile_image.content_type.startswith('image'):
            user.pro_pic = profile_image

        user.save()
        return redirect('profile')
    
    return render(request, 'user/edit_profile.html')

@login_required(login_url='login')
def order(request):
    user=request.user
    orders=Order.objects.filter(user=user).order_by('-id')
    paginator = Paginator(orders, 5)  # Show 10 transactions per page
    page_number = request.GET.get('page')
    
    try:
        orders = paginator.page(page_number)
    except PageNotAnInteger:
        
        orders = paginator.page(1)
    except EmptyPage:
        
        orders = paginator.page(paginator.num_pages)
    return render(request, 'user/order.html',{'orders': orders})

@login_required(login_url='login')
def cancel_order(request, order_id):
    order = Order.objects.get(id=order_id)
    if request.method == 'POST':
        if order.status not in ["cancelled", "delivered"]:
            order.status="cancelled"
            order.save()
        if order.payment_status==1:
            refund_amount=order.Grand_total
            user=request.user
            wallet, created = Wallet.objects.get_or_create(user=user)
            wallet.balance+=refund_amount
            print(wallet.balance)
            wallet.save()
            WalletTransaction.objects.create(user=request.user, amount=refund_amount, transaction_type='credit', transaction_details= "Tiara"+ str(order.id) + " order cancelled")

            
        with transaction.atomic():
            order_items = OrderItem.objects.filter(order=order)
            for order_item in order_items:
                product = order_item.variant
                product.stock += order_item.quantity
                product.save()
        return redirect('order_details', order_id=order_id)
    
@login_required(login_url='login')
def order_details(request,order_id):
    order=Order.objects.get(id=order_id)
    return render(request, 'user/order_details.html',{'order':order})

@login_required(login_url='login')
def wishlist(request):
    wishlist=Wishlist.objects.filter(user=request.user)
    return render(request, 'user/wishlist.html', {'wishlist':wishlist})

@login_required(login_url='login')
def addwishlist(request, variant_id):
    variant = get_object_or_404(Variant, id=variant_id)
    wishlist_item = Wishlist.objects.filter(user=request.user, variant=variant).first()
    if not wishlist_item:
        
        Wishlist.objects.create(user=request.user, variant=variant)
        return redirect('product_details', variant.product.id)
    else:
        messages.warning(request, "This item is already in your wishlist.")
        return redirect('product_details', variant.product.id)

@login_required(login_url='login') 
def removewishlist(request,id):
    variant = get_object_or_404(Variant, id=id)
    wishlist_item = get_object_or_404(Wishlist, user=request.user, variant=variant)
    wishlist_item.delete()
    return redirect('wishlist')

@login_required(login_url='login') 
def wallet(request):
    wallets = Wallet.objects.get(user=request.user)
    all_transactions = WalletTransaction.objects.filter(user=request.user).order_by('-timestamp')
    
    paginator = Paginator(all_transactions, 5)  # Show 10 transactions per page
    page_number = request.GET.get('page')
    
    try:
        transactions = paginator.page(page_number)
    except PageNotAnInteger:
        
        transactions = paginator.page(1)
    except EmptyPage:
        
        transactions = paginator.page(paginator.num_pages)
    
    return render(request, 'user/wallet.html', {'wallets': wallets, 'transactions':transactions})

@login_required(login_url='login')
def coupon(request):
    coupons=Coupon.objects.all()
    return render(request, 'user/coupons.html',{'coupons':coupons})

def invoice(request, id):
    order = get_object_or_404(Order, id=id)
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename=invoice_{id}.pdf'

    p = canvas.Canvas(response)

    # Add Tiara name
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, "TIARA")

    # Add customer details
    p.setFont("Helvetica", 12)
    p.drawString(400, 780, f"Customer: {order.shipping_address.full_name}")
    p.drawString(400, 760, f"Order ID: {order.id}")
    p.drawString(400, 740, f"Order Date: {order.order_date}")

    # Add shipping address details
    p.drawString(50, 720, "Shipping Address:")
    p.drawString(100, 700, f"{order.shipping_address.address}, {order.shipping_address.city}")
    p.drawString(100, 680, f"{order.shipping_address.country} - {order.shipping_address.pincode}")
    p.drawString(100, 660, f"Phone: {order.shipping_address.phone_No}")

    # Add table header
    p.drawString(50, 600, "Item Name")
    p.drawString(300, 600, "Quantity")
    p.drawString(400, 600, "Price")
    p.drawString(500, 600, "Discount_Price")

    # Add order items to the table
    y_position = 580  # Initial y-position for table content
    for item in OrderItem.objects.filter(order=order):
        p.drawString(50, y_position, f"{item.variant.product.productname}")
        p.drawString(300, y_position, f"{item.quantity}")
        p.drawString(400, y_position, f"{item.variant.price}")
        p.drawString(500, y_position, f"{item.variant.discount_price}")
        y_position -= 20

    # Add total amount
    
    total_amount = sum(item.variant.price * item.quantity for item in OrderItem.objects.filter(order=order))
    amount = sum(item.variant.discount_price * item.quantity for item in OrderItem.objects.filter(order=order))
    shipping=order.shipping_charge
    total=total_amount+shipping
    discount_total=amount+shipping
    save=total-discount_total

    p.drawString(400,400, f"Total Amount: {total_amount}")
    p.drawString(400,380, f"Shipping Charge: {shipping}")
    p.drawString(400,360, f"Discount Price: {discount_total}")
    p.drawString(400,340, f"Total Saving: {save}")

    p.showPage()
    p.save()

    return response