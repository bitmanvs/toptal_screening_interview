from decimal import Decimal

from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError

from accounts.models import Role
from orders.models import Coupon, Order, OrderItem, OrderStatus, OrderStatusHistory
from restaurants.models import Meal, Restaurant

# Order lifecycle: which status can move to which, and which role may trigger each target.
# Owner drives processing/in_route/delivered; customer confirms received; both can cancel early.
ALLOWED_TRANSITIONS = {
    OrderStatus.PLACED: {OrderStatus.PROCESSING, OrderStatus.CANCELED},
    OrderStatus.PROCESSING: {OrderStatus.IN_ROUTE, OrderStatus.CANCELED},
    OrderStatus.IN_ROUTE: {OrderStatus.DELIVERED},
    OrderStatus.DELIVERED: {OrderStatus.RECEIVED},
}
ROLE_ALLOWED_TARGETS = {
    OrderStatus.PROCESSING: {Role.OWNER},
    OrderStatus.IN_ROUTE: {Role.OWNER},
    OrderStatus.DELIVERED: {Role.OWNER},
    OrderStatus.RECEIVED: {Role.CUSTOMER},
    OrderStatus.CANCELED: {Role.CUSTOMER, Role.OWNER},
}

def calculate_order_total(subtotal, discount_percentage, tip_amount):
    discount_multiplier = Decimal('1') - (discount_percentage / Decimal('100'))
    discounted_subtotal = subtotal * discount_multiplier
    return discounted_subtotal + tip_amount


@transaction.atomic
def place_order(*, customer, restaurant_id, items, tip_amount=Decimal('0.00'), coupon_code=None):
    restaurant = Restaurant.objects.filter(id=restaurant_id, is_blocked=False).first()
    if restaurant is None:
        raise ValidationError({'restaurant_id': 'Restaurant not found or unavailable.'})

    if not items:
        raise ValidationError({'items': 'At least one meal is required.'})

    coupon = None
    discount_percentage = Decimal('0')
    if coupon_code:
        coupon = Coupon.objects.filter(code=coupon_code, is_active=True).first()
        if coupon is None:
            raise ValidationError({'coupon_code': 'Invalid or inactive coupon.'})
        discount_percentage = coupon.discount_percentage

    meal_ids = [item['meal_id'] for item in items]
    meals = Meal.objects.filter(
        id__in=meal_ids,
        restaurant_id=restaurant_id,
        is_blocked=False,
    )
    meals_by_id = {meal.id: meal for meal in meals}
    
    # Enforce that every requested meal exists, is available, and belongs to this one restaurant.
    if len(meals_by_id) != len(set(meal_ids)):
        raise ValidationError({
            'items': 'All meals must belong to the selected restaurant and be available.',
        })

    subtotal = Decimal('0')
    order_items_data = []

    for item in items:
        meal = meals_by_id[item['meal_id']]
        quantity = item['quantity']
        subtotal += meal.price * quantity
        order_items_data.append({
            'meal': meal,
            'quantity': quantity,
            'unit_price': meal.price,
        })

    total_amount = calculate_order_total(subtotal, discount_percentage, tip_amount)

    order = Order.objects.create(
        customer=customer,
        restaurant=restaurant,
        status=OrderStatus.PLACED,
        tip_amount=tip_amount,
        coupon=coupon,
        total_amount=total_amount,
    )

    OrderItem.objects.bulk_create([
        OrderItem(
            order=order,
            meal=item_data['meal'],
            quantity=item_data['quantity'],
            unit_price=item_data['unit_price'],
        )
        for item_data in order_items_data
    ])

    OrderStatusHistory.objects.create(
        order=order,
        status=OrderStatus.PLACED,
        changed_by=customer,
    )

    return order

@transaction.atomic
def transition_order_status(*, order, new_status, changed_by):
    current_status = order.status
    if new_status not in ALLOWED_TRANSITIONS.get(current_status, set()):
        raise ValidationError({
            'status': f'Cannot transition from {current_status} to {new_status}.',
        })
    if changed_by.role != Role.ADMIN:
        allowed_roles = ROLE_ALLOWED_TARGETS.get(new_status, set())
        if changed_by.role not in allowed_roles:
            raise PermissionDenied('You do not have permission to set this status.')
        if new_status == OrderStatus.CANCELED:
            if changed_by.role == Role.CUSTOMER and order.customer_id != changed_by.id:
                raise PermissionDenied('You can only cancel your own orders.')
            if changed_by.role == Role.OWNER and order.restaurant.owner_id != changed_by.id:
                raise PermissionDenied('You can only cancel orders for your restaurants.')
        if new_status == OrderStatus.RECEIVED and order.customer_id != changed_by.id:
            raise PermissionDenied('You can only mark your own orders as received.')
        if new_status in (OrderStatus.PROCESSING, OrderStatus.IN_ROUTE, OrderStatus.DELIVERED):
            if order.restaurant.owner_id != changed_by.id:
                raise PermissionDenied('You can only update orders for your restaurants.')
    order.status = new_status
    order.save(update_fields=['status'])
    OrderStatusHistory.objects.create(
        order=order,
        status=new_status,
        changed_by=changed_by,
    )
    return order

