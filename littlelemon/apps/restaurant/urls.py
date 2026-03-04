from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('menu', views.MenuItemView.as_view(), name = 'menu-list'),
    path('menu/<int:pk', views.SingleMenuItemView.as_view(), name = 'menu-detail'),
]