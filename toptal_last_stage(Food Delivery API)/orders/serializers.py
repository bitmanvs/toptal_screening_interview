from decimal import Decimal

from rest_framework import serializers

from orders.models import Coupon, Order, OrderItem, OrderStatus, OrderStatusHistory
from orders.services import place_order


class OrderItemInputSerializer(serializers.Serializer):
    meal_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    restaurant_id = serializers.IntegerField()
    items = OrderItemInputSerializer(many=True)
    tip_amount = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=False,
        default=0,
        min_value=Decimal('0'),
    )
    coupon_code = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        request = self.context['request']
        coupon_code = validated_data.pop('coupon_code', None) or None

        return place_order(
            customer=request.user,
            restaurant_id=validated_data['restaurant_id'],
            items=validated_data['items'],
            tip_amount=validated_data.get('tip_amount', 0),
            coupon_code=coupon_code,
        )


class OrderItemSerializer(serializers.ModelSerializer):
    meal_name = serializers.CharField(source='meal.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'meal', 'meal_name', 'quantity', 'unit_price']

class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=OrderStatus.choices)

class OrderStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_email = serializers.EmailField(source='changed_by.email', read_only=True)

    class Meta:
        model = OrderStatusHistory
        fields = ['id', 'status', 'changed_by', 'changed_by_email', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    coupon_code = serializers.CharField(source='coupon.code', read_only=True, default=None)

    class Meta:
        model = Order
        fields = [
            'id',
            'customer',
            'restaurant',
            'status',
            'tip_amount',
            'coupon',
            'coupon_code',
            'total_amount',
            'items',
            'status_history',
            'created_at',
        ]
        read_only_fields = fields

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'discount_percentage', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']