from django.shortcuts import render, get_object_or_404
from .models import MenuItem

# Create your views here.
def home(request):
    return render(request, "home.html")

def menu(request):
    items = MenuItem.objects.all()
    return render(request, "menu.html",{"items": items})

def menu_item_detail(request, pk):
    item = get_object_or_404(MenuItem,pk=pk)
    return render(request, "menu_item_detail.html",{"item": item})

