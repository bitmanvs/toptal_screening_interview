from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import Role
from orders.models import Coupon, OrderStatus
from orders.services import place_order, transition_order_status
from restaurants.models import Meal, Restaurant

User = get_user_model()

DEMO_PASSWORD = 'password123'


class Command(BaseCommand):
    help = (
        'Seed demo data: two owners with restaurants and meals, a returning '
        'customer with a completed order, and a coupon. The "fan_david" '
        'customer is intentionally left out so registration can be shown live.'
    )

    @transaction.atomic
    def handle(self, *args, **options):
        messi = self._owner('messi@worldcup.com')
        yamal = self._owner('yamal@worldcup.com')
        fan_john = self._customer('fan_john@worldcup.com')

        vijs = self._restaurant(
            messi,
            'Vij-s',
            'Contemporary Indian cuisine in South Granville, Vancouver.',
        )
        self._meals(vijs, [
            ('Lamb Popsicles', 'Signature wine-marinated lamb chops', '36.00'),
            ('Jackfruit Curry', 'Slow-cooked jackfruit in coconut curry', '24.00'),
            ('Vegetable Pakoras', 'Crispy chickpea-battered fritters', '12.00'),
            ('Mango Lassi', 'Sweet yogurt mango drink', '7.00'),
        ])

        miku = self._restaurant(
            yamal,
            'Miku Vancouver',
            'Waterfront Japanese restaurant famous for Aburi flame-seared sushi.',
        )
        aburi, _miku_roll, _spicy_tuna, miso = self._meals(miku, [
            ('Aburi Salmon Oshi Sushi', 'Flame-seared pressed salmon sushi', '22.00'),
            ('Miku Roll', 'Prawn tempura, salmon, avocado', '26.00'),
            ('Spicy Tuna Roll', 'Tuna with house spicy sauce', '14.00'),
            ('Miso Soup', 'Traditional soybean broth', '5.00'),
        ])

        Coupon.objects.get_or_create(
            code='WELCOME15',
            defaults={'discount_percentage': Decimal('15.00'), 'is_active': True},
        )

        self._completed_order(fan_john, yamal, miku, aburi, miso)

        self.stdout.write(self.style.SUCCESS('Demo data ready.'))
        self.stdout.write('Owners:    messi@worldcup.com, yamal@worldcup.com (password123)')
        self.stdout.write('Customer:  fan_john@worldcup.com (password123)')
        self.stdout.write('Register fan_david@worldcup.com live to demo sign-up.')

    def _owner(self, email):
        return self._account(email, Role.OWNER)

    def _customer(self, email):
        return self._account(email, Role.CUSTOMER)

    def _account(self, email, role):
        user, created = User.objects.get_or_create(email=email, defaults={'role': role})
        if created:
            user.set_password(DEMO_PASSWORD)
            user.save()
        return user

    def _restaurant(self, owner, name, description):
        restaurant, _ = Restaurant.objects.get_or_create(
            owner=owner,
            name=name,
            defaults={'description': description},
        )
        return restaurant

    def _meals(self, restaurant, rows):
        meals = []
        for name, description, price in rows:
            meal, _ = Meal.objects.get_or_create(
                restaurant=restaurant,
                name=name,
                defaults={'description': description, 'price': Decimal(price)},
            )
            meals.append(meal)
        return meals

    def _completed_order(self, customer, owner, restaurant, aburi, miso):
        if restaurant.orders.filter(customer=customer).exists():
            return

        order = place_order(
            customer=customer,
            restaurant_id=restaurant.id,
            items=[
                {'meal_id': aburi.id, 'quantity': 2},
                {'meal_id': miso.id, 'quantity': 1},
            ],
            tip_amount=Decimal('3.00'),
        )
        transition_order_status(order=order, new_status=OrderStatus.PROCESSING, changed_by=owner)
        transition_order_status(order=order, new_status=OrderStatus.IN_ROUTE, changed_by=owner)
        transition_order_status(order=order, new_status=OrderStatus.DELIVERED, changed_by=owner)
        transition_order_status(order=order, new_status=OrderStatus.RECEIVED, changed_by=customer)
