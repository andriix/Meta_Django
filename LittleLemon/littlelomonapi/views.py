from django.http import HttpResponse
from rest_framework import generics, permissions, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import CategorySerializer, MenuItemSerializer, CartSerializer, OrderSerializer, OrderItemSerializer
from .permissions import IsManager, IsDeliveryCrew, IsCustomer
from django.contrib.auth.models import User, Group
from django.utils import timezone
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

# Basic homepage
def home(request):
    return HttpResponse("<h1>Welcome to Little Lemon API</h1><p>Final task of API course</p>")

# Categories
class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# Menu items: list/create with search, ordering and category filter
class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['price', 'title', 'featured']

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category__slug=category)
        return qs

    def get_permissions(self):
        # Only managers can POST
        if self.request.method == "POST":
            return [IsManager()]
        return super().get_permissions()

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        # Only Managers (or superuser) can update/delete
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsManager()]
        return super().get_permissions()


# Cart views
class CartView(generics.ListCreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user).select_related('menuitem')

    def perform_create(self, serializer):
        # ensure unique_together: if exists -> update quantity
        menuitem_id = self.request.data.get('menuitem_id')
        quantity = int(self.request.data.get('quantity', 1))
        menu = get_object_or_404(MenuItem, id=menuitem_id)
        cart_obj, created = Cart.objects.get_or_create(user=self.request.user, menuitem=menu, defaults={
            'quantity': quantity,
            'unit_price': menu.price,
            'price': menu.price * quantity
        })
        if not created:
            cart_obj.quantity += quantity
            cart_obj.unit_price = menu.price
            cart_obj.price = cart_obj.unit_price * cart_obj.quantity
            cart_obj.save()
        # return created/updated object in response
        return Response(CartSerializer(cart_obj).data, status=status.HTTP_201_CREATED)

class CartClearView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_200_OK)


# Orders
class OrderView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists() or user.is_superuser:
            return Order.objects.all().prefetch_related('orderitem_set')
        if user.groups.filter(name='Delivery crew').exists():
            return Order.objects.filter(delivery_crew=user).prefetch_related('orderitem_set')
        return Order.objects.filter(user=user).prefetch_related('orderitem_set')

    def perform_create(self, serializer):
        user = self.request.user
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            from rest_framework import serializers as drf_serializers
            raise drf_serializers.ValidationError("Cart is empty")

        order = serializer.save(user=user, date=timezone.now(), total=0)
        total = 0
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price
            )
            total += item.price
        order.total = total
        order.save()
        cart_items.delete()

# Single order operations: get, update, delete, and delivery crew patch
class OrderDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Order, pk=pk)

    def get(self, request, pk):
        order = self.get_object(pk)
        user = request.user
        # access rules
        if user.groups.filter(name='Manager').exists() or user.is_superuser:
            pass
        elif user.groups.filter(name='Delivery crew').exists():
            if order.delivery_crew != user:
                return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        else:
            if order.user != user:
                return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        return Response(OrderSerializer(order).data)

    def patch(self, request, pk):
        order = self.get_object(pk)
        user = request.user
        data = request.data

        # Delivery crew can only update status (boolean)
        if user.groups.filter(name='Delivery crew').exists():
            if 'status' in data:
                order.status = bool(data['status'])
                order.save()
                return Response(OrderSerializer(order).data)
            return Response({"detail": "Delivery crew can only update status"}, status=status.HTTP_400_BAD_REQUEST)

        # Manager can update delivery_crew and status
        if user.groups.filter(name='Manager').exists() or user.is_superuser:
            if 'delivery_crew_id' in data:
                try:
                    u = User.objects.get(pk=int(data['delivery_crew_id']))
                    order.delivery_crew = u
                except User.DoesNotExist:
                    return Response({"detail": "User not found"}, status=status.HTTP_400_BAD_REQUEST)
            if 'status' in data:
                order.status = bool(data['status'])
            order.save()
            return Response(OrderSerializer(order).data)

        return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk):
        order = self.get_object(pk)
        user = request.user
        if user.groups.filter(name='Manager').exists() or user.is_superuser:
            order.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)


# Group management endpoints (Manager-only)
class GroupUsersView(APIView):
    permission_classes = [IsManager]

    def get(self, request, group_name):
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            return Response({"detail": "Group not found"}, status=status.HTTP_404_NOT_FOUND)
        users = group.user_set.all()
        data = [{"id": u.id, "username": u.username, "email": u.email} for u in users]
        return Response(data)

    def post(self, request, group_name):
        username = request.data.get('username')
        if not username:
            return Response({"detail": "username required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        group, _ = Group.objects.get_or_create(name=group_name)
        group.user_set.add(user)
        return Response({"detail": "User added"}, status=status.HTTP_201_CREATED)

class GroupUserDetailView(APIView):
    permission_classes = [IsManager]

    def delete(self, request, group_name, user_id):
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            return Response({"detail": "Group not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        group.user_set.remove(user)
        return Response({"detail": "User removed"}, status=status.HTTP_200_OK)
