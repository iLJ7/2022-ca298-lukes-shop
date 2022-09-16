from rest_framework import serializers
from .models import *

class ProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'image']


class BasketItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasketItem
        fields = ['product_id', 'quantity', 'price']


class BasketSerializer(serializers.ModelSerializer):
    items = BasketItemSerializer(many=True, read_only=True, source='basketitem_set')

    class Meta:
        model = Basket
        fields = ['id', 'user_id', 'is_active', 'items']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'basket_id', 'datetime_ordered', 'user_id', "total_price", "shipping_addr"]


class APIUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = APIUser
        fields = ['id','email','username']



class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIUser
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}


    def create(self, validated_data):
        email = validated_data['email']
        username = validated_data['username']
        passsword = validated_data['password'] # Extract the username, email and passwor from the serializer
        new_user = APIUser.objects.create_user(username=username, 
			email=email, password=passsword) # Create a new APIUser
        new_user.save() # Save the new user
        return new_user


class AddBasketItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasketItem
        fields = ['product_id']
    
    def create(self, validated_data):
        product_id = validated_data['product_id']
        request = self.context.get('request', None)
        if request:
            current_user = request.user
            shopping_basket = Basket.objects.filter(user_id=current_user, is_active=True).first()
            if shopping_basket is None:
                shopping_basket = Basket.objects.create(user_id=current_user)
                # Check if the item is already in the basket
            basket_items = BasketItem.objects.filter(product_id=product_id, basket_id=shopping_basket).first()
            if basket_items:
                basket_items.quantity = basket_items.quantity + 1 # if it is already in the basket, add to the quantity
                basket_items.save()
                return basket_items
            else:
                new_basket_item = BasketItem.objects.create(basket_id = shopping_basket, product_id=product_id)
                return new_basket_item
            
        else:
            return None

class RemoveBasketItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasketItem
        fields = ['product_id']


    def create(self, validated_data):
        product_id = validated_data['product_id']
        request = self.context.get('request', None)
        if request:
            current_user = request.user
            shopping_basket = Basket.objects.filter(user_id=current_user, is_active=True).first()
            # Check if the item is already in the basket
            basket_items = BasketItem.objects.filter(product_id=product_id, basket_id=shopping_basket).first()
            if basket_items:
                if basket_items.quantity > 1:
                    basket_items.quantity = basket_items.quantity - 1 # if it is already in the basket, add to the quantity
                    basket_items.save()
                    return basket_items
                else:
                    basket_items.delete()
                    return BasketItem(basket_id=shopping_basket, product_id=product_id, quantity=0)
            else:
                return BasketItem(basket_id=shopping_basket, product_id=product_id, quantity=0)
        else:
            return None



class CheckoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['basket_id', 'shipping_addr']

    def create(self, validated_data):
        request = self.context.get('request', None)
        current_user = request.user
        basket_id = validated_data['basket_id']
        shp = validated_data['shipping_addr']
        # get the sopping basket
        # mark as inactive
        basket_id.is_active = False
        basket_id.save()
        # Get the individual items and show the total
        sbi = BasketItem.objects.filter(basket_id=basket_id)
        total = 0.0
        for item in sbi:
            total += float(item.price())
        # create a new order 
        order = Order.objects.create(basket_id = basket_id, user_id = current_user, shipping_addr =shp, total_price = total )
        # create a new empty basket for the customer 
        new_basket = Basket.objects.create(user_id = current_user)# Create a shopping basket 
        # return the order
        return order
