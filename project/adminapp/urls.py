from django.urls import path
from. import views


urlpatterns = [
    path('',views.admin_login, name="admin_login"),
    path('Dashboard/',views.dashboard, name="dashboard"),
    path('users/', views.users,name="users"),
    path('user_active/<int:id>/',views.user_active, name="useractive"),
    # path('updateuser/<int:id>/',views.update_user,name="updateuser"),
    path('delete_user/<int:id>/',views.delete_user,name="delete_user"),
    
    
    path('category/',views.category,name="category"),
    path('category_active/<int:id>/', views.category_active,name="categoryactive"),
    path('add_category/',views.add_category, name="add_category"),
    path('delete_category/<int:id>/',views.delete_category, name="delete_category"),

    path('variant/',views.variant, name="variant"),
    path('addvariant/', views.add_variant, name="add_variant"),
    path('deletevariant/<int:id>/',views.delete_variant, name="delete_variant"),

    path('product/',views.product,name="product"),
    path('add_product/',views.add_product, name="add_product"),
    # path('product_active/<int:id>/', views.product_active, name="product_active"),
    path('get_product/<int:id>/',views.get_product, name="get_product"),
    path('update_product/<int:id>/', views.update_product, name="update_product"),
    path('delete_product/<int:id>/', views.delete_product, name="delete_product"),

    path('order/', views.order, name="order"),
    path('order_details/<int:id>/', views.order_view, name="order_view"),
    path('change_order_status/<int:order_id>/', views.change_order_status, name='change_order_status'),


    path('coupon/', views.coupons, name="coupons"),
    path('add_coupon/', views.add_coupon, name="addcoupon"),
    path('delete_coupon/<int:id>/', views.delete_coupon,  name="deletecoupon"),
]



