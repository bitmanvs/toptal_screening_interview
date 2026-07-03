import pytest
from django.db import IntegrityError

from accounts.models import Role, User


@pytest.mark.django_db
def test_create_user_with_email():
    user = User.objects.create_user(email='user@example.com', password='secret123')
    assert user.email == 'user@example.com'
    assert user.role == Role.CUSTOMER
    assert user.check_password('secret123')


@pytest.mark.django_db
def test_email_must_be_unique():
    User.objects.create_user(email='dup@example.com', password='secret123')
    with pytest.raises(IntegrityError):
        User.objects.create_user(email='dup@example.com', password='other')


@pytest.mark.django_db
def test_builtin_admin_cannot_be_deleted():
    admin = User.objects.get(email='admin@fooddelivery.local')
    assert admin.is_builtin_admin is True
    with pytest.raises(Exception):
        admin.delete()