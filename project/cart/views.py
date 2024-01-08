from decimal import Decimal
import email
from django.conf import settings
from django.shortcuts import redirect, render
from .models import *
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import razorpay
from project.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
from userdetails.models import *

@login_required(login_url='login')
def cart(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user, is_paid=False)
    cart.summarycart()
    cartitems = CartItem.objects.filter(cart=cart)
    count = cartitems.count()
    return render(request, 'user/cart.html', {'cartitems': cartitems, 'cart': cart, 'count': count})



@login_required(login_url='login')
def add_to_cart(request, product_id):
    user = request.user
    product = get_object_or_404(Product, id=product_id)
    wishlist_item = Wishlist.objects.filter(user=user, product=product).first()
    if wishlist_item:
        wishlist_item.delete()  
    cart, created = Cart.objects.get_or_create(user=user, is_paid=False)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not item_created:
        cart_item.quantity += 1 
        cart_item.save()
    return redirect('product_details', product.id)

@login_required(login_url='login')
def remove_item(request, item_id):
    user=request.user
    cart=Cart.objects.get(user=user)
    cart.discnt=0
    cart.summarycart()
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    return redirect('cart')


def update_quantity(request, cart_id):
    if request.method == 'POST':
        action = request.POST.get('action')
        cart_item = get_object_or_404(CartItem, id=cart_id)

        if action == 'decrement':
            cart_item.quantity = max(1, cart_item.quantity - 1)
        elif action == 'increment':
            if cart_item.quantity < cart_item.product.stock:
                cart_item.quantity += 1
        
        cart_item.save()

        # Update the total for the item
        item_total = cart_item.product.price * cart_item.quantity

        # Update the total for the entire cart
        user = request.user
        cart = Cart.objects.get(user=user)
        cart.summarycart()

    return redirect('cart')



def apply_coupon(request):
    user = request.user
    cart = Cart.objects.get(user=user)
    if request.method == 'POST':
        code = request.POST.get('code')
        try:
            coupon = Coupon.objects.get(code=code)      
            order_exists = Order.objects.filter(user=user).exists()
            
            if coupon and cart.total > coupon.minimum_amount:
                if code=='TiaraFirst' and not order_exists:
                    grand_total = cart.grand_total
                    discount = (grand_total * coupon.dis_per) / 100
                    cart.discnt = discount
                    cart.summarycart()
                    request.session['code'] = code
                    return redirect('address')
                if code =='Tiara1000' and order_exists:
                    grand_total = cart.grand_total
                    discount = (grand_total * coupon.dis_per) / 100  
                    cart.discnt = discount
                    cart.summarycart()
                    request.session['code'] = code
                       
                    return redirect('address')

                else:
                    messages.error(request, 'Coupon already applied')
            else:
                messages.error(request,'does not meet conditions')
                    
                                
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid Coupon Code or coupon not available')
    return redirect('address')

def cancel_coupon(request):
    user=request.user
    cart=Cart.objects.get(user=user)
    cart.discnt=0
    cart.save()
    return redirect('address')

    

@login_required(login_url='login')
def address_page(request):
    user = request.user
    addresses=Address.objects.filter(user=user)
    cartitem=CartItem.objects.all()
    cart=Cart.objects.get(user=user)
    cart.summarycart()
    code=request.session.get('code')
    coupon = None
    try:
        coupon=Coupon.objects.get(code=code)
    except:
        if cartitem:
            return render(request, 'user/address.html', {'addresses': addresses, 'cart':cart, 'coupon':coupon})

        messages.error(request,"Your cart is empty. Add items to the cart before proceeding to the checkout.")
        return redirect('cart')
    return render(request, 'user/address.html', {'addresses': addresses, 'cart':cart, 'coupon':coupon})

def add_address(request):
    if request.method=='POST':
        
        fullname=request.POST.get("name",'')
        address=request.POST.get('address','')
        city=request.POST.get('city','')
        pincode=request.POST.get('zip','')
        country=request.POST.get('country','')
        phone_no=request.POST.get('phone','')
        if not fullname.strip() and not address.strip() and  not city.strip() and not pincode.strip() and not country.strip() and not phone_no.strip():
            messages.error(request,"please enter non empty value")
            return redirect('address')
        address=Address.objects.create(user=request.user,full_name=fullname,address=address,city=city,pincode=pincode,country=country,phone_No=phone_no)
        address.save()

    if 'profile' in request.META.get('HTTP_REFERER'):
    
        return redirect('profile')
    else:
        return redirect('address')
    

def remove_address(request,id):
    address=Address.objects.get(id=id)
    address.delete()
    
    if 'profile' in request.META.get('HTTP_REFERER'):
    
        return redirect('profile')
    else:
        return redirect('address')
    

def get_address(request,id):
    address=Address.objects.get(id=id)
    
    return render(request, 'user/edit_address.html',{'address':address})

@login_required(login_url='login')
def update_address(request,id):
    address=Address.objects.get(id=id)
    if request.method=="POST":
        address.full_name=request.POST.get("name")
        address.address=request.POST.get("address")
        address.city=request.POST.get("city")
        address.pincode=request.POST.get("pincode")
        address.country=request.POST.get("country")
        address.phone_no=request.POST.get("phone_no")
        address.save()
    if 'profile' in request.META.get('HTTP_REFERER'):
    
        return redirect('profile')
    else:
        return redirect('address')   

@login_required(login_url='login')
def cod(request,address_id):
    user=request.user
    cart=Cart.objects.get(user=user)
    cart.summarycart()
    address=Address.objects.get(id=address_id)
    request.session['address_id']='address'   
    return render(request,'user/cod.html',{ 'cart':cart, 'address':address})

@login_required(login_url='login')
def wallet_payment(request, address_id):
    user=request.user
    cart=Cart.objects.get(user=user)
    address = Address.objects.get(id=address_id)
    request.session['address_id'] = address_id
    return render(request, 'user/walletpayment.html', {'cart': cart, 'address': address})

@login_required(login_url='login')
def pay_wallet(request):
    user=request.user
    address=request.session.get('address_id')
    addrss=Address.objects.get(id=address)
    cartitems=CartItem.objects.all()
    cart=Cart.objects.get(user=user)
    wallet=Wallet.objects.get(user=user)
    if wallet.balance>=cart.grand_total:
        wallet.balance=wallet.balance-cart.grand_total
        
        wallet.save()
        order ,created = Order.objects.get_or_create(
        user=request.user, 
        address=addrss,
        total_amount=cart.total,
        Grand_total=cart.grand_total,
        payment_status=1,  
        status='confirmed',
        payment_method='Wallet',
        discount=cart.discnt
        )
        order.save()
        WalletTransaction.objects.create(user=user, amount=order.Grand_total, transaction_type='debit')

        cart.discount=0
        for cart_item in cartitems:
            order_item=OrderItem.objects.create(order=order, product=cart_item.product, quantity=cart_item.quantity, product_price=cart_item.product.price)
            product = order_item.product
            product.stock -= order_item.quantity
            product.save()
        cartitems.delete()
        return redirect('order_confirmation', order.id)
    messages.error(request,'Insufficient balance on your wallet')
    return redirect('wallet_payment', address_id=address)
    
@login_required(login_url='login')
def place_order(request, address_id):
    user=request.user
    email=user.email
    cart_items = CartItem.objects.all()
    cart=Cart.objects.get(user=user)
    cart.summarycart()
    address=Address.objects.get(id=address_id)
    order ,created = Order.objects.get_or_create(
        user=request.user, 
        address=address,
        total_amount=cart.total,
        Grand_total=cart.grand_total,
        payment_status=3,  
        status='confirmed',
        payment_method='Cash On Delivery',
        discount=cart.discnt
    )
    order.save()
    cart.discount=0
    for cart_item in cart_items:
        order_item=OrderItem.objects.create(order=order, product=cart_item.product, quantity=cart_item.quantity, product_price=cart_item.product.price)
        product = order_item.product
        product.stock -= order_item.quantity
        product.save()
    cart_items.delete()
    send_mail("Your Order is Confirmed", 'Message body goes here', EMAIL_HOST_USER, [email], fail_silently=True)
    return redirect('order_confirmation', order.id)

   

@login_required(login_url='login')
def order_confirmation(request,order_id):
    order=Order.objects.get(id=order_id)
    transaction= request.GET.get('transaction_id')
    return render(request, 'user/orderconfirmation.html', {'order':order, 'transaction':transaction})

@login_required(login_url='login')
def cancel_order(request, order_id):
    order=order.object.get(id=order_id)
    if order.payment_status=='1':
        order.status="False"
        order.save()
        for order_item in order.items.all():
            product = order_item.product
            product.stock += order_item.quantity
            product.save()
    
    return redirect('orderdetails')
        


def online_payment(request,address_id):
    user=request.user
    cart_items = CartItem.objects.all()
    cart=Cart.objects.get(user=user)
    cart.summarycart()
    address=Address.objects.get(id=address_id)
    client = razorpay.Client(auth=(settings.KEY,  settings.SECRET))
    amount = float(cart.grand_total)*100

    payment = {
        'amount': amount,
        'currency': 'INR',
        'payment_capture': 1  # Auto capture payment
    }

   
    clnt_order = client.order.create(data=payment)

    order = Order.objects.create(
        user=request.user,  
        address=address,
        total_amount=cart.total,
        Grand_total=cart.grand_total,
        payment_status=1,  
        status='confirmed',
        payment_method='Online Payment',
        discount=cart.discnt
    )
    for cart_item in cart_items:
        order_item=OrderItem.objects.create(order=order, product=cart_item.product, quantity=cart_item.quantity, product_price=cart_item.product.price)
        product = order_item.product
        product.stock -= order_item.quantity
        product.save()
    cart_items.delete()
    return render(request, 'user/onlinepayment.html', {'address': address, 'clnt_order': clnt_order, 'order': order, 'cart':cart})

