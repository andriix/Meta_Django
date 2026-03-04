from rest_framework import serializers
from .models import Menu, Booking
from django.contrib.auth.models import User

class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ['id', 'title', 'price', 'inventory']
        read_only_fields = ['id']
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("negative price")
        return value

class BookingSerializer(serializers.ModelSerializer):
     class Meta:
          model = Booking
          fields = ['id', 'name', 'no_of_guests', 'booking_date']
          read_only_fields = ['id']

class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ['url', 'username', 'email', 'groups']

