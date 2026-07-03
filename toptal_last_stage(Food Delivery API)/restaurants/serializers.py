from rest_framework import serializers

from accounts.models import Role
from restaurants.models import Meal, Restaurant


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = [
            'id',
            'owner',
            'name',
            'description',
            'is_blocked',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'owner': {'required': False},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')

        # Only admins may reassign ownership or block/unblock; lock these for everyone else.
        if request and request.user.is_authenticated and request.user.role != Role.ADMIN:
            self.fields['owner'].read_only = True
            self.fields["is_blocked"].read_only = True
    
    def validate(self, attrs):
        request = self.context.get("request")
        is_creating = self.instance is None
        owner_missing = not attrs.get("owner")

        if request and request.user.role == Role.ADMIN and is_creating and owner_missing:
            raise serializers.ValidationError(
                {"owner": "An owner is required when an administrator creates a restaurant."}
            )
        return attrs

    def create(self, validated_data):
        request = self.context['request']
        if request.user.role == Role.OWNER:
            validated_data['owner'] = request.user
        return super().create(validated_data)


class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = [
            'id',
            'restaurant',
            'name',
            'description',
            'price',
            'is_blocked',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated and request.user.role != Role.ADMIN:
            self.fields["is_blocked"].read_only = True
    
    def validate_restaurant(self, restaurant):
        request = self.context['request']
        user = request.user

        if user.role == Role.ADMIN:
            return restaurant

        if restaurant.owner_id != user.id:
            raise serializers.ValidationError(
                'You can only manage meals for your own restaurants.'
            )
        return restaurant
