from rest_framework.routers import DefaultRouter

from orders.views import OrderViewSet, CouponViewSet

router = DefaultRouter()
router.register('orders', OrderViewSet, basename='order')
router.register('coupons', CouponViewSet, basename='coupon')

urlpatterns = router.urls