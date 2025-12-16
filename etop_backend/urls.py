from django.urls import path, include
from .views import (
    ElectricCarViewSet, 
    ManufacturerViewSet, 
    CarColorViewSet,
    SubscribeView,
    UnsubscribeView,
    SubscriptionPreferencesView,
    SalesAssociateListView,
    EmailSubscriberViewSet,
)
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
# Car inventory endpoints
router.register('electric-cars', ElectricCarViewSet, basename='electric-car')
router.register('car-manufacturer', ManufacturerViewSet, basename='car-manufacturer')
router.register('car-colors', CarColorViewSet, basename='car-colors')

# Email subscription admin endpoints
router.register('admin/email-subscribers', EmailSubscriberViewSet, basename='email-subscriber')


urlpatterns = [
    # Include all router URLs
    path('', include(router.urls)),
    
    # Email subscription public endpoints
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('unsubscribe/', UnsubscribeView.as_view(), name='unsubscribe'),
    path('subscription/preferences/', SubscriptionPreferencesView.as_view(), name='subscription-preferences'),
    path('sales-associates/', SalesAssociateListView.as_view(), name='sales-associates'),
    
    # About Us public endpoints
    # path('about-us/', PublicAboutUsView.as_view(), name='public-about-us'),
    # path('about-us/team/', PublicTeamMembersView.as_view(), name='public-team'),
    # path('about-us/gallery/', PublicDealershipGalleryView.as_view(), name='public-gallery'),
    
    # # Additional About Us endpoints from ViewSet
    # path('about-us/location/', AboutUsViewSet.as_view({'get': 'location'}), name='public-location'),
    # path('about-us/public/', AboutUsViewSet.as_view({'get': 'public'}), name='public-about-us-v2'),
]