from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Role
from orders.models import Coupon, Order, OrderStatus
from restaurants.models import Meal, Restaurant

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def customer():
    return User.objects.create_user(
        email='customer@example.com',
        password='password123',
        role=Role.CUSTOMER,
    )


@pytest.fixture
def other_customer():
    return User.objects.create_user(
        email='othercustomer@example.com',
        password='password123',
        role=Role.CUSTOMER,
    )


@pytest.fixture
def owner():
    return User.objects.create_user(
        email='owner@example.com',
        password='password123',
        role=Role.OWNER,
    )


@pytest.fixture
def other_owner():
    return User.objects.create_user(
        email='otherowner@example.com',
        password='password123',
        role=Role.OWNER,
    )


@pytest.fixture
def admin_user():
    return User.objects.create_user(
        email='admin@example.com',
        password='password123',
        role=Role.ADMIN,
    )


@pytest.fixture
def restaurant(owner):
    return Restaurant.objects.create(
        owner=owner,
        name='Spice Garden',
        description='Indian cuisine',
        is_blocked=False,
    )


@pytest.fixture
def other_restaurant(other_owner):
    return Restaurant.objects.create(
        owner=other_owner,
        name='Other Kitchen',
        description='Different owner',
        is_blocked=False,
    )


@pytest.fixture
def burger(restaurant):
    return Meal.objects.create(
        restaurant=restaurant,
        name='Burger',
        description='Classic burger',
        price=Decimal('10.00'),
        is_blocked=False,
    )


@pytest.fixture
def fries(restaurant):
    return Meal.objects.create(
        restaurant=restaurant,
        name='Fries',
        description='Crispy fries',
        price=Decimal('5.00'),
        is_blocked=False,
    )


@pytest.fixture
def other_meal(other_restaurant):
    return Meal.objects.create(
        restaurant=other_restaurant,
        name='Pasta',
        description='From another restaurant',
        price=Decimal('12.00'),
        is_blocked=False,
    )


@pytest.fixture
def coupon():
    return Coupon.objects.create(
        code='SAVE10',
        discount_percentage=Decimal('10.00'),
        is_active=True,
    )


def place_order_payload(restaurant, meals, tip_amount='0.00', coupon_code=None):
    payload = {
        'restaurant_id': restaurant.id,
        'items': [
            {'meal_id': meal.id, 'quantity': quantity}
            for meal, quantity in meals
        ],
        'tip_amount': tip_amount,
    }
    if coupon_code is not None:
        payload['coupon_code'] = coupon_code
    return payload


@pytest.mark.django_db
def test_customer_places_order(api_client, customer, restaurant, burger, fries):
    api_client.force_authenticate(user=customer)

    response = api_client.post(
        '/api/orders/',
        place_order_payload(
            restaurant,
            [(burger, 2), (fries, 1)],
            tip_amount='0.00',
        ),
        format='json',
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['status'] == OrderStatus.PLACED
    assert response.data['customer'] == customer.id
    assert response.data['restaurant'] == restaurant.id
    assert len(response.data['items']) == 2
    assert len(response.data['status_history']) == 1
    assert response.data['status_history'][0]['status'] == OrderStatus.PLACED
    assert response.data['status_history'][0]['changed_by'] == customer.id

    order = Order.objects.get(id=response.data['id'])
    assert order.status == OrderStatus.PLACED
    assert order.items.count() == 2


@pytest.mark.django_db
def test_order_total_with_tip_and_coupon(
    api_client,
    customer,
    restaurant,
    burger,
    fries,
    coupon,
):
    api_client.force_authenticate(user=customer)

    # Subtotal: (10.00 * 2) + 5.00 = 25.00
    # Discount 10%: 22.50
    # Tip: 2.50
    # Total: 25.00
    response = api_client.post(
        '/api/orders/',
        place_order_payload(
            restaurant,
            [(burger, 2), (fries, 1)],
            tip_amount='2.50',
            coupon_code='SAVE10',
        ),
        format='json',
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert Decimal(response.data['total_amount']) == Decimal('25.00')
    assert response.data['tip_amount'] == '2.50'
    assert response.data['coupon_code'] == 'SAVE10'


@pytest.mark.django_db
def test_place_order_rejects_meals_from_different_restaurants(
    api_client,
    customer,
    restaurant,
    burger,
    other_meal,
):
    api_client.force_authenticate(user=customer)

    response = api_client.post(
        '/api/orders/',
        {
            'restaurant_id': restaurant.id,
            'items': [
                {'meal_id': burger.id, 'quantity': 1},
                {'meal_id': other_meal.id, 'quantity': 1},
            ],
            'tip_amount': '0.00',
        },
        format='json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'items' in response.data
    assert Order.objects.count() == 0


@pytest.mark.django_db
def test_full_order_status_flow(
    api_client,
    customer,
    owner,
    restaurant,
    burger,
):
    api_client.force_authenticate(user=customer)
    create_response = api_client.post(
        '/api/orders/',
        place_order_payload(restaurant, [(burger, 1)]),
        format='json',
    )
    order_id = create_response.data['id']

    transitions = [
        (owner, 'processing'),
        (owner, 'in_route'),
        (owner, 'delivered'),
        (customer, 'received'),
    ]

    for user, next_status in transitions:
        api_client.force_authenticate(user=user)
        response = api_client.patch(
            f'/api/orders/{order_id}/',
            {'status': next_status},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == next_status

    detail_response = api_client.get(f'/api/orders/{order_id}/')
    assert detail_response.status_code == status.HTTP_200_OK
    assert detail_response.data['status'] == OrderStatus.RECEIVED
    assert len(detail_response.data['status_history']) == 5
    assert [entry['status'] for entry in detail_response.data['status_history']] == [
        OrderStatus.PLACED,
        OrderStatus.PROCESSING,
        OrderStatus.IN_ROUTE,
        OrderStatus.DELIVERED,
        OrderStatus.RECEIVED,
    ]


@pytest.mark.django_db
def test_customer_cancels_placed_order(api_client, customer, restaurant, burger):
    api_client.force_authenticate(user=customer)
    create_response = api_client.post(
        '/api/orders/',
        place_order_payload(restaurant, [(burger, 1)]),
        format='json',
    )
    order_id = create_response.data['id']

    response = api_client.patch(
        f'/api/orders/{order_id}/',
        {'status': OrderStatus.CANCELED},
        format='json',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['status'] == OrderStatus.CANCELED


@pytest.mark.django_db
def test_owner_cancels_processing_order(api_client, customer, owner, restaurant, burger):
    api_client.force_authenticate(user=customer)
    create_response = api_client.post(
        '/api/orders/',
        place_order_payload(restaurant, [(burger, 1)]),
        format='json',
    )
    order_id = create_response.data['id']

    api_client.force_authenticate(user=owner)
    api_client.patch(
        f'/api/orders/{order_id}/',
        {'status': OrderStatus.PROCESSING},
        format='json',
    )

    response = api_client.patch(
        f'/api/orders/{order_id}/',
        {'status': OrderStatus.CANCELED},
        format='json',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['status'] == OrderStatus.CANCELED


@pytest.mark.django_db
def test_cannot_cancel_order_in_route(api_client, customer, owner, restaurant, burger):
    api_client.force_authenticate(user=customer)
    create_response = api_client.post(
        '/api/orders/',
        place_order_payload(restaurant, [(burger, 1)]),
        format='json',
    )
    order_id = create_response.data['id']

    api_client.force_authenticate(user=owner)
    api_client.patch(
        f'/api/orders/{order_id}/',
        {'status': OrderStatus.PROCESSING},
        format='json',
    )
    api_client.patch(
        f'/api/orders/{order_id}/',
        {'status': OrderStatus.IN_ROUTE},
        format='json',
    )

    response = api_client.patch(
        f'/api/orders/{order_id}/',
        {'status': OrderStatus.CANCELED},
        format='json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'status' in response.data


@pytest.mark.django_db
def test_customer_cannot_set_processing_status(
    api_client,
    customer,
    restaurant,
    burger,
):
    api_client.force_authenticate(user=customer)
    create_response = api_client.post(
        '/api/orders/',
        place_order_payload(restaurant, [(burger, 1)]),
        format='json',
    )
    order_id = create_response.data['id']

    response = api_client.patch(
        f'/api/orders/{order_id}/',
        {'status': OrderStatus.PROCESSING},
        format='json',
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_other_owner_cannot_update_foreign_order(
    api_client,
    customer,
    other_owner,
    restaurant,
    burger,
):
    api_client.force_authenticate(user=customer)
    create_response = api_client.post(
        '/api/orders/',
        place_order_payload(restaurant, [(burger, 1)]),
        format='json',
    )
    order_id = create_response.data['id']
    api_client.force_authenticate(user=other_owner)
    response = api_client.patch(
        f'/api/orders/{order_id}/',
        {'status': OrderStatus.PROCESSING},
        format='json',
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_order_list_scoped_for_customer(
    api_client,
    customer,
    other_customer,
    restaurant,
    burger,
):
    api_client.force_authenticate(user=customer)
    own_order = api_client.post(
        '/api/orders/',
        place_order_payload(restaurant, [(burger, 1)]),
        format='json',
    ).data['id']

    api_client.force_authenticate(user=other_customer)
    other_order = api_client.post(
        '/api/orders/',
        place_order_payload(restaurant, [(burger, 1)]),
        format='json',
    ).data['id']

    api_client.force_authenticate(user=customer)
    response = api_client.get('/api/orders/')

    assert response.status_code == status.HTTP_200_OK
    order_ids = [order['id'] for order in response.data]
    assert own_order in order_ids
    assert other_order not in order_ids


@pytest.mark.django_db
def test_order_list_scoped_for_owner(
    api_client,
    customer,
    owner,
    other_owner,
    restaurant,
    other_restaurant,
    burger,
    other_meal,
):
    api_client.force_authenticate(user=customer)
    own_restaurant_order = api_client.post(
        '/api/orders/',
        place_order_payload(restaurant, [(burger, 1)]),
        format='json',
    ).data['id']
    other_restaurant_order = api_client.post(
        '/api/orders/',
        place_order_payload(other_restaurant, [(other_meal, 1)]),
        format='json',
    ).data['id']

    api_client.force_authenticate(user=owner)
    response = api_client.get('/api/orders/')

    assert response.status_code == status.HTTP_200_OK
    order_ids = [order['id'] for order in response.data]
    assert own_restaurant_order in order_ids
    assert other_restaurant_order not in order_ids


@pytest.mark.django_db
def test_admin_sees_all_orders(
    api_client,
    customer,
    admin_user,
    restaurant,
    burger,
):
    api_client.force_authenticate(user=customer)
    order_id = api_client.post(
        '/api/orders/',
        place_order_payload(restaurant, [(burger, 1)]),
        format='json',
    ).data['id']

    api_client.force_authenticate(user=admin_user)
    response = api_client.get('/api/orders/')

    assert response.status_code == status.HTTP_200_OK
    order_ids = [order['id'] for order in response.data]
    assert order_id in order_ids


@pytest.mark.django_db
def test_owner_cannot_place_order(api_client, owner, restaurant, burger):
    api_client.force_authenticate(user=owner)

    response = api_client.post(
        '/api/orders/',
        place_order_payload(restaurant, [(burger, 1)]),
        format='json',
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Order.objects.count() == 0