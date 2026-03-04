from django.shortcuts import render
from rest_framework import generics
from .models import Menu
from .serializers import MenuSerializer

# Create your views here.
def home(request):
    return render(request, 'restaurant/home.html')

class MenuItemView(generics.ListCreateAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer