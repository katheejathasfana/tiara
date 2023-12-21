from django.urls import path

from . import views

urlpatterns = [
  
    path('',views.cart, name='cart'),
    path('add_to _cart/<int:product_id>/',views.add_to_cart, name='add_to_cart'),
    path('remove_item/<int:item_id>/',views.remove_item,name='remove_item'),
    path('update_quantity/<int:cart_id>/', views.update_quantity , name="update_quantity"),


    path('address/',views.address_page,name="address"),
    path('add_address/',views.add_address, name="add_address"),
    path('remove_address/<int:id>',views.remove_address, name="remove_address"),
    path('get_address/<int:id>/', views.get_address, name='get_address'),
    path('update_address/<int:id>/', views.update_address, name='update_address'),

    path('payment/<int:address_id>/', views.payment, name="payment"),
    path('place_order/<int:address_id>/',views.place_order, name="place_order"),
    path('orderconfirmation/<int:order_id>/', views.order_confirmation, name="order_confirmation")

   
    
]