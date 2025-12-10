from django.urls import path, include
from .views import ElectricCarViewSet, ManufacturerViewSet, CarColorViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('electric-cars', ElectricCarViewSet, basename='electric-car'),
router.register('car-manufacturer', ManufacturerViewSet, basename='car-manufacturer')
router.register('car-colors', CarColorViewSet, basename='car-colors')

urlpatterns = [
    path('', include(router.urls)),
]
