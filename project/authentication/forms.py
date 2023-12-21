# from django import forms

# from django.contrib.auth import authenticate
# from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm


# class UserLoginForm(AuthenticationForm):
#     username = forms.EmailField(
#         widget=forms.TextInput(
#             attrs={"class": "mb-2", "placeholder": "Your email", "id": "login-username"}
#         )
#     )
#     password = forms.CharField(
#         widget=forms.PasswordInput(
#             attrs={
#                 "class": "mb-2",
#                 "placeholder": "Your password",
#                 "id": "login-password",
#             }
#         )
#     )

#     def clean(self):
#         username = self.cleaned_data.get("username")
#         password = self.cleaned_data.get("password")
#         print(username)
#         print(password)
#         if username is not None and password:
#             self.user_cache = authenticate(
#                 self.request, email=username, password=password
#             )
#             if self.user_cache is None:
#                 raise self.get_invalid_login_error()
#             else:
#                 self.confirm_login_allowed(self.user_cache)

#         return self.cleaned_data

