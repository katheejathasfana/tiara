from django.urls import path

from . import views

urlpatterns = [
  
    path('',views.profile, name='profile'),
    path('edit_profile', views.edit_profile, name="edit_profile"),

    path('myorders/', views.order, name="orders"),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('order_details/<int:order_id>/', views.order_details, name="order_details"),
    

    path('wishlist/', views.wishlist, name="wishlist"),
    path('add_wishlist/<int:variant_id>/', views.addwishlist, name="addwishlist"),
    path('remove_wishlist/<int:id>/', views.removewishlist, name="removewishlist"),

    path('wallet/',views.wallet, name="wallet"),
    path('coupon/',views.coupon, name="coupon"),

    path('invoice/<int:id>/', views.invoice, name='invoice'),

]