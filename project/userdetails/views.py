from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from cart.models import *

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

    return render(request, 'user/order.html', {'orders': orders})

@login_required(login_url='login')
def cancel_order(request, order_id):
    order = Order.objects.get(id=order_id)
    if request.method == 'POST':
        if order.status != "cancelled" or order.status != "delivered":
            order.status="cancelled"
            order.save()
            
        return redirect('order_details', order_id=order_id)
    

def order_details(request,order_id):
    order=Order.objects.get(id=order_id)
    return render(request, 'user/order_details.html',{'order':order})