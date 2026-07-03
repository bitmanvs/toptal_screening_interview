from rest_framework import viewsets

from accounts.models import Role
from restaurants.models import Meal, Restaurant
from restaurants.permissions import MealPermission, RestaurantPermission
from restaurants.serializers import MealSerializer, RestaurantSerializer


class RestaurantViewSet(viewsets.ModelViewSet):
    serializer_class = RestaurantSerializer
    permission_classes = [RestaurantPermission]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Restaurant.objects.none()
        user = self.request.user
        queryset = Restaurant.objects.select_related('owner')

        if user.role == Role.ADMIN:
            return queryset

        if user.role == Role.OWNER:
            if self.action in ('update', 'partial_update', 'destroy'):
                return queryset
            if self.action in ('list', 'retrieve'):
                return queryset.filter(is_blocked=False)
            return queryset.filter(owner=user)

        return queryset.filter(is_blocked=False)


class MealViewSet(viewsets.ModelViewSet):
    serializer_class = MealSerializer
    permission_classes = [MealPermission]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Meal.objects.none()
        user = self.request.user
        queryset = Meal.objects.select_related('restaurant', 'restaurant__owner')

        restaurant_id = self.request.query_params.get('restaurant')
        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)

        if user.role == Role.ADMIN:
            return queryset

        if user.role == Role.OWNER:
            if self.action in ('update', 'partial_update', 'destroy'):
                return queryset
            if self.action in ('list', 'retrieve'):
                return queryset.filter(
                    is_blocked=False,
                    restaurant__is_blocked=False,
                )
            return queryset.filter(restaurant__owner=user)

        return queryset.filter(
            is_blocked=False,
            restaurant__is_blocked=False,
        )
