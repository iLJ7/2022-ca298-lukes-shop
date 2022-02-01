from django.http import HttpResponse
from django.shortcuts import render
from .models import *

def index(request):
    
    products = Product.objects.all()

    return render(request, 'index.html', {'products':products})

def product_individual(request, prodid):
    product = Product.objects.get(id=prodid)

    return render(request, 'product_individual.html', {'product':product})

# -------------------

from django.views.generic import CreateView
from django.contrib.auth import login, logout
from lukeshop.forms import *
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required

class UserSignupView(CreateView):
    model = APIUser
    form_class = UserSignupForm
    template_name = 'user_signup.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('/')

class UserLoginView(LoginView):
    template_name='login.html'

def logout_user(request):
    logout(request)
    return redirect("/")

def add_to_basket(request, prodid):
    user = request.user
    # is there a shopping basket for the user 
    basket = Basket.objects.filter(user_id=user, is_active=True).first()
    if not basket:
        # create a new one
        basket = Basket(user_id = user).save()
    # get the product 
    product = Product.objects.get(id=prodid)
    sbi = BasketItem.objects.filter(basket_id=basket, product_id = product).first()
    if sbi is None:
        # there is no basket item for that product 
        # create one 
        sbi = BasketItem(basket_id=basket, product_id = product).save()
    else:
        # a basket item already exists 
        # just add 1 to the quantity
        sbi.quantity = sbi.quantity+1
        sbi.save()
    return render(request, 'product_individual.html', {'product': product, 'added':True})