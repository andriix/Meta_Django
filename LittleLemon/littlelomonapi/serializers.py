from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']

    def create(self, validated_data):
        cat_id = validated_data.pop('category_id', None)
        if cat_id:
            validated_data['category_id'] = cat_id
        return super().create(validated_data)

class CartSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    menuitem = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'menuitem', 'menuitem_id', 'quantity', 'unit_price', 'price']
        read_only_fields = ['unit_price', 'price']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be > 0")
        return value

    def create(self, validated_data):
        menuitem_id = validated_data.pop('menuitem_id')
        try:
            menu = MenuItem.objects.get(id=menuitem_id)
        except MenuItem.DoesNotExist:
            raise serializers.ValidationError({"menuitem_id": "Menu item not found"})
        unit_price = menu.price
        quantity = validated_data.get('quantity', 1)
        validated_data['unit_price'] = unit_price
        validated_data['price'] = unit_price * quantity
        validated_data['menuitem'] = menu
        # user will be set in view.perform_create
        return super().create(validated_data)

class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'menuitem', 'quantity', 'unit_price', 'price']

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    delivery_crew = serializers.StringRelatedField(read_only=True)
    order_items = OrderItemSerializer(source='orderitem_set', many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'order_items']
        read_only_fields = ['total', 'date', 'order_items']
