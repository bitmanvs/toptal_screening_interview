from rest_framework.routers import DefaultRouter

from restaurants.views import MealViewSet, RestaurantViewSet

router = DefaultRouter()
router.register('restaurants', RestaurantViewSet, basename='restaurant')
router.register('meals', MealViewSet, basename='meal')

urlpatterns = router.urls