from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ElectricCarViewSet, 
    ManufacturerViewSet, 
    CarColorViewSet,
    SubscribeView,
    UnsubscribeView,
    SubscriptionPreferencesView,
    SalesAssociateListView,
    EmailSubscriberViewSet,
    # Service Booking Views
    CustomerVehicleViewSet,
    ServiceBookingViewSet,
    ServiceReminderViewSet,
    PublicServiceBookingView,
    ServiceAvailabilityView,
    ServiceStatisticsView,
    AdminServiceBookingViewSet,
)

router = DefaultRouter()
# Car inventory endpoints
router.register('electric-cars', ElectricCarViewSet, basename='electric-car')
router.register('car-manufacturer', ManufacturerViewSet, basename='car-manufacturer')
router.register('car-colors', CarColorViewSet, basename='car-colors')

# Email subscription admin endpoints
router.register('admin/email-subscribers', EmailSubscriberViewSet, basename='email-subscriber')

# Service Booking endpoints
router.register('customer-vehicles', CustomerVehicleViewSet, basename='customer-vehicle')
router.register('service-bookings', ServiceBookingViewSet, basename='service-booking')
router.register('service-reminders', ServiceReminderViewSet, basename='service-reminder')

# Admin service booking endpoints
router.register('admin/service-bookings', AdminServiceBookingViewSet, basename='admin-service-booking')

urlpatterns = [
    # Include all router URLs
    path('', include(router.urls)),
    
    # Email subscription public endpoints
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('unsubscribe/', UnsubscribeView.as_view(), name='unsubscribe'),
    path('subscription/preferences/', SubscriptionPreferencesView.as_view(), name='subscription-preferences'),
    path('sales-associates/', SalesAssociateListView.as_view(), name='sales-associates'),
    
    # Service Booking public endpoints
    path('public/book-service/', PublicServiceBookingView.as_view(), name='public-book-service'),
    path('service/availability/', ServiceAvailabilityView.as_view(), name='service-availability'),
    path('service/statistics/', ServiceStatisticsView.as_view(), name='service-statistics'),
    
    # Service Booking user endpoints
    path('my-vehicles/neta-eligible/', 
         CustomerVehicleViewSet.as_view({'get': 'neta_eligible'}), 
         name='neta-eligible-vehicles'),
    path('my-vehicles/km-service-eligible/', 
         CustomerVehicleViewSet.as_view({'get': 'km_service_eligible'}), 
         name='km-service-eligible-vehicles'),
    path('my-bookings/upcoming/', 
         ServiceBookingViewSet.as_view({'get': 'upcoming'}), 
         name='upcoming-bookings'),
    path('my-bookings/pending/', 
         ServiceBookingViewSet.as_view({'get': 'pending'}), 
         name='pending-bookings'),
    path('my-bookings/<int:pk>/cancel/', 
         ServiceBookingViewSet.as_view({'post': 'cancel'}), 
         name='cancel-booking'),
]