from rest_framework import serializers
from .models import Menu
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

class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ['url', 'username', 'email', 'groups']