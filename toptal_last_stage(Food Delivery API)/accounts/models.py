from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class Role(models.TextChoices):
    CUSTOMER = 'customer', 'Customer'
    OWNER = 'owner', 'Restaurant Owner'
    ADMIN = 'admin', 'Administrator'


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', Role.ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )
    is_blocked = models.BooleanField(default=False)
    is_builtin_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ['email']

    def __str__(self):
        return self.email

    @property
    def is_customer(self):
        return self.role == Role.CUSTOMER

    @property
    def is_owner(self):
        return self.role == Role.OWNER

    @property
    def is_admin(self):
        return self.role == Role.ADMIN

    # The seeded built-in admin must never be deletable (enforced at the model layer).
    def delete(self, *args, **kwargs):
        if self.is_builtin_admin:
            raise models.ProtectedError(
                'Built-in admin account cannot be deleted.',
                self,
            )
        super().delete(*args, **kwargs)