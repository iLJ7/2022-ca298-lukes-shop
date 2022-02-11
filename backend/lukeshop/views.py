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

@login_required
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
        # create one \
        sbi = BasketItem(basket_id=basket, product_id = product).save()
    else:
        # a basket item already exists 
        # just add 1 to the quantity
        sbi.quantity = sbi.quantity+1
        sbi.save()
    return render(request, 'product_individual.html', {'product': product, 'added':True})

@login_required

def show_basket(request):
    # get the user object
    # does the shopping basket exist?
    # load all shopping basket items
    # display on page
    user = request.user
    basket = Basket.objects.filter(user_id=user, is_active=True).first()
    if basket is None:
        return render(request, 'basket.html', {'empty':True})
    else:
        sbi = BasketItem.objects.filter(basket_id=basket)
        # is this list empty
        if sbi.exists():
            return render(request, 'basket.html', {'basket':basket, 'sbi':sbi})
        else:
            return render(request, 'basket.html', {'empty':True})

@login_required
def remove_item(request, sbi):
    basketitem = BasketItem.objects.get(id=sbi)
    if basketitem is None:
        return redirect("/basket") # if error redirect to shopping basket
    
    else:
        if basketitem.quantity > 1:
            basketitem.quantity = basketitem.quantity-1
            basketitem.save() # save our changes to the db
        
        else:
            basketitem.delete() # delete the basket item
    
    return redirect("/basket")

@login_required
def order(request):
    # load in all the data we need: user, basket, items
    user = request.user
    basket = Basket.objects.filter(user_id=user, is_active=True).first()
    if basket is None:
        return redirect("/")
    
    sbi = BasketItem.objects.filter(basket_id=basket)
    if not sbi.exists(): # if there are no items
        return redirect("/")
    
    if request.method == "POST":
        # check if valid
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user_id = user
            order.basket_id = basket
            total = 0.0
            for item in sbi:
                total += float(item.price())
            
            order.total_price = total
            order.save()
            basket.is_active = False
            basket.save()
            return render(request, 'ordercomplete.html', {'order':order, 'basket':basket, 'sbi':sbi})
        
        else:
            return render(request, 'orderform.html', {'form':form, 'basket':basket, 'sbi':sbi})

    else:
        # show the form
        form = OrderForm()
        return render(request, 'orderform.html', {'form':form, 'basket':basket, 'sbi':sbi})
    # check that the data is okay.
    # POST or GET
