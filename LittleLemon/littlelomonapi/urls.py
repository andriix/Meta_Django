from django.urls import path, include
from . import views

urlpatterns = [
    path('categories/', views.CategoryView.as_view(), name='category-list'),
    path('menu-items/', views.MenuItemView.as_view(), name='menuitem-list'),
    path('menu-items/<int:pk>/', views.SingleMenuItemView.as_view(), name='menuitem-detail'),
    path('cart/menu-items/', views.CartView.as_view(), name='cart-list'),
    path('cart/menu-items/clear/', views.CartClearView.as_view(), name='cart-clear'),
    path('orders/', views.OrderView.as_view(), name='order-list'),
]