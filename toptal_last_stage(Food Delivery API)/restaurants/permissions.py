from rest_framework.permissions import SAFE_METHODS, BasePermission

from accounts.models import Role


class RestaurantPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated or user.is_blocked:
            return False
        if request.method in SAFE_METHODS:
            return True
        return user.role in (Role.OWNER, Role.ADMIN)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.role == Role.ADMIN:
            return True
        return obj.owner_id == request.user.id


class MealPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated or user.is_blocked:
            return False
        if request.method in SAFE_METHODS:
            return True
        return user.role in (Role.OWNER, Role.ADMIN)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.role == Role.ADMIN:
            return True
        return obj.restaurant.owner_id == request.user.id
