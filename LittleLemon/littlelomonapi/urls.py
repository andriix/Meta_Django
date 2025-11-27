from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.CategoryView.as_view(), name='category-list'),
    path('menu-items/', views.MenuItemView.as_view(), name='menuitem-list'),
    path('menu-items/<int:pk>/', views.SingleMenuItemView.as_view(), name='menuitem-detail'),
    path('cart/menu-items/', views.CartView.as_view(), name='cart-list'),
    path('cart/menu-items/clear/', views.CartClearView.as_view(), name='cart-clear'),
    path('orders/', views.OrderView.as_view(), name='order-list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    # groups management
    path('groups/<str:group_name>/users/', views.GroupUsersView.as_view(), name='group-users'),
    path('groups/<str:group_name>/users/<int:user_id>/', views.GroupUserDetailView.as_view(), name='group-user-detail'),
]
