from rest_framework.permissions import BasePermission

from accounts.models import Role


class IsNotBlocked(BasePermission):
    message = 'This account is blocked.'

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return True
        return not user.is_blocked


class IsCustomer(BasePermission):
    message = 'Customer role required.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and not request.user.is_blocked
            and request.user.role == Role.CUSTOMER
        )


class IsOwner(BasePermission):
    message = 'Restaurant owner role required.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and not request.user.is_blocked
            and request.user.role == Role.OWNER
        )


class IsAdmin(BasePermission):
    message = 'Administrator role required.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and not request.user.is_blocked
            and request.user.role == Role.ADMIN
        )