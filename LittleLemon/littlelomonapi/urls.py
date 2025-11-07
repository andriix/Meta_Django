from django.urls import path, include
from . import views

urlpatterns = [
    path('categories/', views.CategoryView.as_view(), name='category-list'),
    path('menu-items/', views.MenuItemView.as_view(), name='menuitem-list'),
    path('menu-items/<int:pk>/', views.SingleMenuItemView.as_view(), name='menuitem-detail'),
]