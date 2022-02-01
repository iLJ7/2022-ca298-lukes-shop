from django.urls import path
from . import views
from .models import *
from lukeshop import forms

urlpatterns = [
   path('', views.index, name="index"),
   path('products/<int:prodid>', views.product_individual, name="individual_product"),
   path('register/', views.UserSignupView.as_view(), name="register"),
   path('login/', views.LoginView.as_view(template_name="login.html", authentication_form=forms.UserLoginForm)),
   path('addbasket/<int:prodid>', views.add_to_basket, name="add_basket"),
]
