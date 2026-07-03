import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_register_customer(api_client):
    response = api_client.post(
        '/api/auth/register/',
        {'email': 'newuser@example.com', 'password': 'password123'},
        format='json',
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['email'] == 'newuser@example.com'
    assert response.data['role'] == 'customer'


@pytest.mark.django_db
def test_register_duplicate_email_returns_400(api_client):
    User.objects.create_user(email='dup@example.com', password='password123')
    response = api_client.post(
        '/api/auth/register/',
        {'email': 'dup@example.com', 'password': 'password123'},
        format='json',
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_login_returns_jwt_tokens(api_client):
    User.objects.create_user(email='login@example.com', password='password123')
    response = api_client.post(
        '/api/auth/login/',
        {'email': 'login@example.com', 'password': 'password123'},
        format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
    assert 'refresh' in response.data


@pytest.mark.django_db
def test_login_invalid_credentials_returns_401(api_client):
    User.objects.create_user(email='login@example.com', password='password123')
    response = api_client.post(
        '/api/auth/login/',
        {'email': 'login@example.com', 'password': 'wrongpassword'},
        format='json',
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_blocked_user_cannot_login(api_client):
    user = User.objects.create_user(email='blocked@example.com', password='password123')
    user.is_blocked = True
    user.save()
    response = api_client.post(
        '/api/auth/login/',
        {'email': 'blocked@example.com', 'password': 'password123'},
        format='json',
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_me_returns_current_user(api_client):
    user = User.objects.create_user(email='me@example.com', password='password123')
    api_client.force_authenticate(user=user)
    response = api_client.get('/api/auth/me/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['email'] == 'me@example.com'
    assert response.data['role'] == 'customer'


@pytest.mark.django_db
def test_blocked_user_cannot_access_me(api_client):
    user = User.objects.create_user(email='blocked@example.com', password='password123')
    user.is_blocked = True
    user.save()
    api_client.force_authenticate(user=user)
    response = api_client.get('/api/auth/me/')
    assert response.status_code == status.HTTP_403_FORBIDDEN