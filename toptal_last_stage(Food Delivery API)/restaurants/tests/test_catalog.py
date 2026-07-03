import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Role
from restaurants.models import Meal, Restaurant

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def customer(api_client):
    user = User.objects.create_user(
        email='customer@example.com',
        password='password123',
        role=Role.CUSTOMER,
    )
    api_client.force_authenticate(user=user)
    return user


@pytest.fixture
def owner(api_client):
    user = User.objects.create_user(
        email='owner@example.com',
        password='password123',
        role=Role.OWNER,
    )
    api_client.force_authenticate(user=user)
    return user


@pytest.fixture
def other_owner():
    return User.objects.create_user(
        email='otherowner@example.com',
        password='password123',
        role=Role.OWNER,
    )

@pytest.fixture
def admin(api_client):
    user = User.objects.create_user(
        email='admin@example.com',
        password='password123',
        role=Role.ADMIN,
    )
    api_client.force_authenticate(user=user)
    return user

@pytest.fixture
def active_restaurant(owner):
    return Restaurant.objects.create(
        owner=owner,
        name='Spice Garden',
        description='Indian cuisine',
        is_blocked=False,
    )


@pytest.fixture
def blocked_restaurant(owner):
    return Restaurant.objects.create(
        owner=owner,
        name='Closed Kitchen',
        description='Temporarily unavailable',
        is_blocked=True,
    )

@pytest.mark.django_db
def test_admin_create_restaurant_without_owner_returns_400(api_client, admin):
    response = api_client.post(
        '/api/restaurants/',
        {'name': 'No Owner', 'description': 'missing owner'},
        format='json',
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'owner' in response.data


@pytest.mark.django_db
def test_admin_create_restaurant_with_owner(api_client, admin, other_owner):
    response = api_client.post(
        '/api/restaurants/',
        {'name': 'Admin Made', 'description': 'x', 'owner': other_owner.id},
        format='json',
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['owner'] == other_owner.id

@pytest.mark.django_db
def test_owner_cannot_block_own_restaurant(api_client, owner, active_restaurant):
    response = api_client.patch(
        f'/api/restaurants/{active_restaurant.id}/',
        {'is_blocked': True},
        format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data['is_blocked'] is False


@pytest.mark.django_db
def test_admin_can_block_restaurant(api_client, admin, active_restaurant):
    api_client.force_authenticate(user=admin)
    response = api_client.patch(
        f'/api/restaurants/{active_restaurant.id}/',
        {'is_blocked': True},
        format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data['is_blocked'] is True

@pytest.mark.django_db
def test_admin_updates_any_restaurant(api_client, admin, active_restaurant):
    api_client.force_authenticate(user=admin)
    response = api_client.patch(
        f'/api/restaurants/{active_restaurant.id}/',
        {'description': 'Edited by admin'},
        format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    active_restaurant.refresh_from_db()
    assert active_restaurant.description == 'Edited by admin'


@pytest.mark.django_db
def test_admin_deletes_any_meal(api_client, admin, active_restaurant):
    api_client.force_authenticate(user=admin)
    meal = Meal.objects.create(
        restaurant=active_restaurant,
        name='Temp',
        description='to delete',
        price='9.99',
    )
    response = api_client.delete(f'/api/meals/{meal.id}/')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Meal.objects.filter(id=meal.id).exists()

@pytest.mark.django_db
def test_customer_lists_active_restaurants(api_client, customer, active_restaurant, blocked_restaurant):
    response = api_client.get('/api/restaurants/')

    assert response.status_code == status.HTTP_200_OK
    restaurant_ids = [item['id'] for item in response.data]
    assert active_restaurant.id in restaurant_ids
    assert blocked_restaurant.id not in restaurant_ids


@pytest.mark.django_db
def test_owner_creates_restaurant(api_client, owner):
    response = api_client.post(
        '/api/restaurants/',
        {
            'name': 'Urban Bites',
            'description': 'Street food',
        },
        format='json',
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['name'] == 'Urban Bites'
    assert response.data['owner'] == owner.id
    assert Restaurant.objects.filter(name='Urban Bites', owner=owner).exists()


@pytest.mark.django_db
def test_owner_updates_own_restaurant(api_client, owner, active_restaurant):
    response = api_client.patch(
        f'/api/restaurants/{active_restaurant.id}/',
        {'description': 'Updated description'},
        format='json',
    )

    assert response.status_code == status.HTTP_200_OK
    active_restaurant.refresh_from_db()
    assert active_restaurant.description == 'Updated description'


@pytest.mark.django_db
def test_owner_cannot_update_another_owners_restaurant(api_client, owner, other_owner):
    restaurant = Restaurant.objects.create(
        owner=other_owner,
        name='Other Place',
        description='Not yours',
    )

    response = api_client.patch(
        f'/api/restaurants/{restaurant.id}/',
        {'description': 'Attempted change'},
        format='json',
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    restaurant.refresh_from_db()
    assert restaurant.description == 'Not yours'


@pytest.mark.django_db
def test_blocked_restaurant_hidden_from_customer(api_client, customer, blocked_restaurant):
    response = api_client.get('/api/restaurants/')

    assert response.status_code == status.HTTP_200_OK
    restaurant_ids = [item['id'] for item in response.data]
    assert blocked_restaurant.id not in restaurant_ids


@pytest.mark.django_db
def test_owner_creates_meal_on_own_restaurant(api_client, owner, active_restaurant):
    response = api_client.post(
        '/api/meals/',
        {
            'restaurant': active_restaurant.id,
            'name': 'Butter Chicken',
            'description': 'Creamy tomato curry',
            'price': '14.99',
        },
        format='json',
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['name'] == 'Butter Chicken'
    assert Meal.objects.filter(
        restaurant=active_restaurant,
        name='Butter Chicken',
    ).exists()


@pytest.mark.django_db
def test_customer_cannot_create_restaurant(api_client, customer):
    response = api_client.post(
        '/api/restaurants/',
        {
            'name': 'Customer Cafe',
            'description': 'Should not be allowed',
        },
        format='json',
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not Restaurant.objects.filter(name='Customer Cafe').exists()