from rest_framework import serializers
from .models import Rating
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth.models import User

class RatingSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset = User.objects.all()
        default=serializers.CurrentUserDefault()
    )