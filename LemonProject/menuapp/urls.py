from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("menu/", views.menu, name="menu"),
    path("menu/<int:pk>/", views.menu_item_detail, name="menu_item_detail"),
]