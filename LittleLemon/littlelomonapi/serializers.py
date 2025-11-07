from rest_framwork import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price',
                  'featured', 'category']
