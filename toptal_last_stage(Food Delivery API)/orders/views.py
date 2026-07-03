from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import Role
from accounts.permissions import IsAdmin, IsCustomer, IsNotBlocked
from orders.models import Order, Coupon
from orders.serializers import (
    CouponSerializer,
    OrderCreateSerializer,
    OrderSerializer,
    OrderStatusUpdateSerializer,
)
from orders.services import transition_order_status

class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated, IsNotBlocked]
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_permissions(self):
        if self.action == 'create':
            return [IsCustomer()]
        return super().get_permissions()

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Order.objects.none()
        user = self.request.user
        queryset = Order.objects.select_related(
            'customer',
            'restaurant',
            'coupon',
        ).prefetch_related(
            'items__meal',
            'status_history__changed_by',
        )

        if user.role == Role.ADMIN:
            return queryset

        if user.role == Role.OWNER:
            return queryset.filter(restaurant__owner=user)

        return queryset.filter(customer=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        if self.action in ('partial_update', 'update'):
            return OrderStatusUpdateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        output_serializer = OrderSerializer(order)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def partial_update(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        transition_order_status(
            order=order,
            new_status=serializer.validated_data["status"],
            changed_by=request.user,
        )
        
        order.refresh_from_db()
        return Response(OrderSerializer(order).data)
    
    # Orders aren't fully editable; PUT and PATCH both perform a single status transition.
    def update(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
    
class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdmin]