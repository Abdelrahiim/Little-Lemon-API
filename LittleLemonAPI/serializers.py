from rest_framework import serializers
from .models import MenuItem, Category, Cart, Order, OrderItem
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


# ---------------------------------------------------------------
class CategorySerializer(serializers.ModelSerializer):
    # ------------------------------
    class Meta:
        model = Category
        fields = ['slug']


# ---------------------------------------------------------------
class MenuItemSerializer(serializers.ModelSerializer):
    # ------------------------------
    category = CategorySerializer(read_only= True)
    category_id = serializers.IntegerField(write_only = True)
    class Meta():
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category','category_id']



# ---------------------------------------------------------------
class CartHelpSerializer(serializers.ModelSerializer):
    # ------------------------------
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price']


# ---------------------------------------------------------------
class CartSerializer(serializers.ModelSerializer):
    menuitem = CartHelpSerializer()

    # ------------------------------
    class Meta:
        model = Cart
        fields = ['menuitem', 'quantity', 'price']


# ---------------------------------------------------------------
class CartAddSerializer(serializers.ModelSerializer):
    # ------------------------------
    class Meta:
        model = Cart
        fields = ['menuitem', 'quantity']
        extra_kwargs = {
            'quantity': {'min_value': 1}
        }


# ---------------------------------------------------------------
class CartRemoveSerializer(serializers.ModelSerializer):
    # ------------------------------
    class Meta:
        model = Cart
        fields = ['menuitem']


# ---------------------------------------------------------------
class UserSerializer(serializers.ModelSerializer):
    # ------------------------------
    class Meta:
        model = User
        fields = ['username']


# ---------------------------------------------------------------
class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    # ------------------------------
    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total', 'delivery_crew', 'date']


# ---------------------------------------------------------------
class SingleOrderHelperSerailizer(serializers.ModelSerializer):
    # ------------------------------
    class Meta:
        model = MenuItem
        fields = ['title', 'price']


# ---------------------------------------------------------------
class SingleOrderSerializer(serializers.ModelSerializer):
    menuitem = SingleOrderHelperSerailizer()

    # ------------------------------
    class Meta:
        model = OrderItem
        fields = ['menuitem', 'quantity']


# ---------------------------------------------------------------
class OrderPutSerializer(serializers.ModelSerializer):
    # ------------------------------
    class Meta:
        model = Order
        fields = ['delivery_crew']


# ---------------------------------------------------------------
class MangerListSerializer(serializers.ModelSerializer):
    # ------------------------------
    class Meta:
        model = User
        fields = ['username', 'email']
