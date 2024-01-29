from django.urls import path

from . import views

urlpatterns = [
  
    path('',views.cart, name='cart'),
    path('add_to _cart/<int:id>/',views.add_to_cart, name='add_to_cart'),
    path('remove_item/<int:item_id>/',views.remove_item,name='remove_item'),
    path('update_quantity/<int:cart_id>/', views.update_quantity , name="update_quantity"),

    path('apply_coupon/', views.apply_coupon, name="applycoupon"),
    path('cancelcoupon/', views.cancel_coupon, name="cancelcoupon"),

    path('address/',views.address_page,name="address"),
    path('add_address/',views.add_address, name="add_address"),
    path('remove_address/<int:id>',views.remove_address, name="remove_address"),
    path('get_address/<int:id>/', views.get_address, name='get_address'),
    path('update_address/<int:id>/', views.update_address, name='update_address'),

    path('cod/<int:address_id>/', views.cod, name="cod"),
    path('onlinepayment/<int:id>/',views.online_payment, name="onlinepayment"),
    path('wallet_payment/<int:id>/',views.wallet_payment, name="wallet_payment"),
    path('paywallet/<int:id>/', views.pay_wallet, name="paywallet"),


    path('place_order/',views.place_order, name="place_order"),
    path('orderconfirmation/<int:order_id>/', views.order_confirmation, name="order_confirmation")
   
    
]