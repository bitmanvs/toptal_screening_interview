from django.contrib.auth.hashers import make_password
from django.db import migrations

BUILTIN_ADMIN_EMAIL = "admin@fooddelivery.local"
BUILTIN_ADMIN_PASSWORD = "Admin12345!"


def create_builtin_admin(apps, schema_editor):
    User = apps.get_model("accounts", "User")

    # Idempotent: never overwrite an existing account with this email on re-runs.
    if User.objects.filter(email=BUILTIN_ADMIN_EMAIL).exists():
        return

    User.objects.create(
        email=BUILTIN_ADMIN_EMAIL,
        password=make_password(BUILTIN_ADMIN_PASSWORD),
        role="admin",
        is_builtin_admin=True,
        is_staff=True,
        is_superuser=True,
        is_active=True,
    )


def delete_builtin_admin(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.filter(email=BUILTIN_ADMIN_EMAIL, is_builtin_admin=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_builtin_admin, delete_builtin_admin),
    ]