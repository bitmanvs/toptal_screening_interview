import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Role
from orders.models import Coupon

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(api_client):
    user = User.objects.create_user(
        email='admin@example.com',
        password='password123',
        role=Role.ADMIN,
    )
    api_client.force_authenticate(user=user)
    return user


@pytest.mark.django_db
def test_admin_creates_owner_user(api_client, admin_user):
    response = api_client.post(
        '/api/users/',
        {
            'email': 'newowner@example.com',
            'password': 'password123',
            'role': Role.OWNER,
        },
        format='json',
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['email'] == 'newowner@example.com'
    assert response.data['role'] == Role.OWNER

    created_user = User.objects.get(email='newowner@example.com')
    assert created_user.check_password('password123')


@pytest.mark.django_db
def test_admin_blocks_user(api_client, admin_user):
    user = User.objects.create_user(
        email='blockme@example.com',
        password='password123',
        role=Role.CUSTOMER,
    )

    response = api_client.patch(
        f'/api/users/{user.id}/',
        {'is_blocked': True},
        format='json',
    )

    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.is_blocked is True


@pytest.mark.django_db
def test_cannot_delete_builtin_admin(api_client, admin_user):
    builtin_admin = User.objects.create_user(
        email='builtin@example.com',
        password='password123',
        role=Role.ADMIN,
        is_builtin_admin=True,
    )

    response = api_client.delete(f'/api/users/{builtin_admin.id}/')

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert User.objects.filter(id=builtin_admin.id).exists()


@pytest.mark.django_db
def test_non_admin_cannot_list_users(api_client):
    customer = User.objects.create_user(
        email='customer@example.com',
        password='password123',
        role=Role.CUSTOMER,
    )
    api_client.force_authenticate(user=customer)

    response = api_client.get('/api/users/')

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_admin_creates_coupon(api_client, admin_user):
    response = api_client.post(
        '/api/coupons/',
        {
            'code': 'SAVE10',
            'discount_percentage': '10.00',
            'is_active': True,
        },
        format='json',
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['code'] == 'SAVE10'
    assert Coupon.objects.filter(code='SAVE10').exists()