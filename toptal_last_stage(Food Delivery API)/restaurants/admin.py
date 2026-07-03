from django.contrib import admin

from restaurants.models import Meal, Restaurant


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'is_blocked', 'created_at']
    list_filter = ['is_blocked']
    search_fields = ['name', 'owner__email']


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ['name', 'restaurant', 'price', 'is_blocked', 'created_at']
    list_filter = ['is_blocked', 'restaurant']
    search_fields = ['name', 'restaurant__name']