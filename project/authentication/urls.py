from django.urls import path
from . import views
urlpatterns = [
    path('',views.home, name='home'),
    path('login/',views.signin, name="login"),
    path('signup/',views.signup,name="signup"),
    path('logout/',views.signout,name="logout"),
   
    path('verification/<str:email>/', views.verification,name="verification"),
    path('forgetpassword/', views.forgetpassword, name="forgetpassword"),
    path('resendotp/<str:email>/', views.resend_otp,name="resendotp"),
    path('otpverify/<str:email>/', views.otp_verify,name="otp_verify"),
    path('reset_password/<str:email>/', views.resetpassword, name="resetpassword"),
    path('product_details/<int:id>', views.product_details,  name="product_details"),
    path('products/',views.products, name="products"),
    path('category/<int:id>', views.category_product , name="categories"),
    
]