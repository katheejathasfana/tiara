from decimal import Decimal
from django.shortcuts import redirect, render
from .models import *
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

# Create your views here.
def summarycart(cartitems):
    total = sum(item.product.price * item.quantity for item in cartitems)
    total_quantity=sum(item.quantity for item in cartitems)
    shipping_cost=Decimal(49.00)
    Grand_total=total+shipping_cost
    return total,Grand_total,total_quantity


@login_required(login_url='login')
def cart(request):
    cartitems=CartItem.objects.all()
    total,Grand_total,_=summarycart(cartitems)
    return render(request,'user/cart.html',{'cartitems':cartitems , 'total':total, 'Grand_total':Grand_total})


@login_required(login_url='login')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user, is_paid=False)

    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not item_created:
        cart_item.quantity += 1 
        cart_item.save()

    return redirect('products')

@login_required(login_url='login')
def remove_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    return redirect('cart')

def update_quantity(request, cart_id):
    if request.method == 'POST':
        action = request.POST.get('action')
        cart_item = CartItem.objects.get(id=cart_id)

        if action == 'decrement':
            cart_item.quantity = max(1, cart_item.quantity - 1)
        elif action == 'increment':
            if cart_item.quantity < cart_item.product.stock:
                cart_item.quantity += 1

        cart_item.save()
        return redirect('cart')


@login_required(login_url='login')
def address_page(request):
    user = request.user
    addresses=Address.objects.filter(user=user)
    cartitem=CartItem.objects.all()
    total,Grand_total,total_quantity=summarycart(cartitem)
    if cartitem:
        return render(request, 'user/address.html', {'addresses': addresses,'total':total, 'total_quantity':total_quantity,'Grand_total':Grand_total},)
    else:
        messages.error(request,"Your cart is empty. Add items to the cart before proceeding to the checkout.")
        return redirect('cart')

def add_address(request):
    if request.method=='POST':
        
        fullname=request.POST.get("name")
        address=request.POST.get('address')
        city=request.POST.get('city')
        pincode=request.POST.get('zip')
        country=request.POST.get('country')
        phone_no=request.POST.get('phone')
        address=Address.objects.create(user=request.user,full_name=fullname,address=address,city=city,pincode=pincode,country=country,phone_No=phone_no)
        address.save()
        return redirect('address')
    

def remove_address(request,id):
    address=Address.objects.get(id=id)
    address.delete()
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
    #     if redirect_to == 'page1':
    #         return redirect('page1')  # Replace 'page1' with the actual URL name for your first page
    #     elif redirect_to == 'page2':
    #         return redirect('page2')  # Replace 'page2' with the actual URL name for your second page

    # return redirect('address')
    return redirect('address')
    

@login_required(login_url='login')
def payment(request,address_id):
    cartitem=CartItem.objects.all()
    total,Grand_total,total_quantity=summarycart(cartitem)
    address=Address.objects.get(id=address_id)
    
    return render(request,'user/cod.html',{'address':address, 'total':total, 'total_quantity':total_quantity,'Grand_total':Grand_total})



@login_required(login_url='login')
def place_order(request, address_id):
    
    cart_items = CartItem.objects.all()
    total, Grand_total, total_quantity = summarycart(cart_items)
    address=Address.objects.get(id=address_id)
    order, created = Order.objects.get_or_create(user=request.user, is_paid=False,total_amount =total, Grand_total=Grand_total,address=address)
    order.status = 'confirmed'
    order.is_paid = False
    order.save()
    for item in cart_items:
        
        product =item.product
        quantity =item.quantity
        
        order_item=OrderItem.objects.create(order=order,product=product, quantity=quantity)
        product=Product.objects.get(productname=product)
        product.stock -= quantity
        product.save()
       
    cart_items.delete()


    return redirect('order_confirmation',order_id=order.id)

   

@login_required(login_url='login')
def order_confirmation(request,order_id):
    order=Order.objects.get(id=order_id)
    cart_items = CartItem.objects.all()
    total, Grand_total, total_quantity = summarycart(cart_items)
    order_items = OrderItem.objects.filter(order=order)
    
    return render(request, 'user/orderconfirmation.html', {'order':order, 'total':total,  'total_quantity':total_quantity,'order_items':order_items})

@login_required(login_url='login')
def cancel_order(request, order_id):
    order=order.object.get(id=order_id)
    if order.status=='True':
        order.status="False"
        order.save()
        for order_item in order.items.all():
            product = order_item.product
            product.stock_quantity += order_item.quantity
            product.save()
    
    return redirect('orderdetails')
        


