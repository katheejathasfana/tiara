# # utils.py
# import random
# import string
# from django.core.mail import send_mail
# from . import views

# def generate_otp():
    
#     return ''.join(random.choices(string.digits, k=6))

# def send_otp(email, otp):
    
#     subject = 'Your OTP for Registration'
#     message = f'Your OTP is: {otp}'
#     from_email = 'tiara@gmail.com'
#     recipient_list = [email]

#     send_mail(subject, message, from_email, recipient_list)
