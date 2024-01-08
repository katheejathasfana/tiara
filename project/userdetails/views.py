from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from cart.models import *
from django.db import transaction
from . models import *
from adminapp.models import *
from django.shortcuts import get_object_or_404
from django.contrib import messages
# Create your views here.
@login_required(login_url='login')
def profile(request):
    return render(request, 'user/profile_dtls.html')

@login_required(login_url='login')
def edit_profile(request):
    user=request.user
    if request.method=='POST':
        user.name = request.POST.get('name', user.name)
        user.phone_Number = request.POST.get('phone_Number', user.phone_Number)
        print(user.phone_Number)
        user.date_of_birth = request.POST.get('date_of_birth', user.date_of_birth)
        profile_image = request.FILES.get('profile_image')
        if profile_image:
            user.pro_pic = profile_image
        user.save()
        return redirect('profile')
    return render(request, 'user/edit_profile.html')

@login_required(login_url='login')
def order(request):
    user=request.user
    orders=Order.objects.filter(user=user).order_by('-id')
    return render(request, 'user/order.html',{'orders': orders})

@login_required(login_url='login')
def cancel_order(request, order_id):
    order = Order.objects.get(id=order_id)
    if request.method == 'POST':
        if order.status not in ["cancelled", "delivered"]:
            order.status="cancelled"
            order.save()
        if order.payment_method=='Online payment' or 'Wallet':
            refund_amount=order.Grand_total
            user=request.user
            wallet, created = Wallet.objects.get_or_create(user=user)
            wallet.balance+=refund_amount
            print(wallet.balance)
            wallet.save()
            WalletTransaction.objects.create(user=request.user, amount=refund_amount, transaction_type='credit')

            
        with transaction.atomic():
            order_items = OrderItem.objects.filter(order=order)
            for order_item in order_items:
                product = order_item.product
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
def addwishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product).first()
    if not wishlist_item:
        
        Wishlist.objects.create(user=request.user, product=product)
        return redirect('wishlist')
    else:
        messages.warning(request, "This item is already in your wishlist.")

        return redirect('wishlist')

@login_required(login_url='login') 
def removewishlist(request,product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item = get_object_or_404(Wishlist, user=request.user, product=product)
    wishlist_item.delete()
    return redirect('wishlist')

def wallet(request):

    try:
        wallets = Wallet.objects.get(user=request.user)
    except Wallet.DoesNotExist:
        wallets = 0
    transactions=WalletTransaction.objects.get(user=request.user)
    return render(request, 'user/wallet.html', {'wallets': wallets, 'transactions':transactions})

@login_required(login_url='login')
def coupon(request):
    coupons=Coupon.objects.all()
    return render(request, 'user/coupons.html',{'coupons':coupons})