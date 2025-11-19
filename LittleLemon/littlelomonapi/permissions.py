from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.groups.filter(name='Manager').exists() or request.user.is_superuser)
        )


class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.groups.filter(name='Delivery crew').exists()
        )


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and not (
                request.user.groups.filter(name='Manager').exists()
                or request.user.groups.filter(name='Delivery crew').exists()
            )
        )
