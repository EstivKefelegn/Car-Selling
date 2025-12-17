from django.urls import path, include
from .views import (  
    AboutUsViewSet,
    TeamMemberViewSet,
    DealershipPhotoViewSet,
    PublicAboutUsView,
    PublicTeamMembersView,
    PublicDealershipGalleryView,
    EventRegistrationViewSet,
    EventCategoryViewSet,
    EventViewSet,
    UpcomingEventsView,
    FeaturedEventsView,
    LatestNewsView,
    FeaturedNewsView,
    NewsViewSet,
    FinanceInformationPageViewSet,
    FinanceFAQViewSet,
    FinanceOfferViewSet,
    FinanceCalculatorViewSet,
    FinanceDocumentViewSet,
    FinancePartnerViewSet,
    FinanceComparisonViewSet,
)
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
# Email subscription admin endpoints
router.register(r'news', NewsViewSet, basename='news')

# About Us admin endpoints
router.register('admin/about-us', AboutUsViewSet, basename='about-us')
router.register('admin/team-members', TeamMemberViewSet, basename='team-members')
router.register('admin/dealership-photos', DealershipPhotoViewSet, basename='dealership-photos')
router.register(r'categories', EventCategoryViewSet, basename='eventcategory')
router.register(r'events', EventViewSet, basename='event')
router.register(r'registrations', EventRegistrationViewSet, basename='eventregistration')
router.register(r'pages', FinanceInformationPageViewSet, basename='finance-page')
router.register(r'faqs', FinanceFAQViewSet, basename='finance-faq')
router.register(r'offers', FinanceOfferViewSet, basename='finance-offer')
router.register(r'calculators', FinanceCalculatorViewSet, basename='finance-calculator')
router.register(r'documents', FinanceDocumentViewSet, basename='finance-document')
router.register(r'partners', FinancePartnerViewSet, basename='finance-partner')
router.register(r'comparison', FinanceComparisonViewSet, basename='finance-comparison')  # New


urlpatterns = [
    path('', include(router.urls)),
    
    
    path('about-us/', PublicAboutUsView.as_view(), name='public-about-us'),
    path('about-us/team/', PublicTeamMembersView.as_view(), name='public-team'),
    path('about-us/gallery/', PublicDealershipGalleryView.as_view(), name='public-gallery'),
    
    path('about-us/location/', AboutUsViewSet.as_view({'get': 'location'}), name='public-location'),
    path('about-us/public/', AboutUsViewSet.as_view({'get': 'public'}), name='public-about-us-v2'),
    path('events/upcoming/', UpcomingEventsView.as_view(), name='upcoming-events'),
    path('events/featured/', FeaturedEventsView.as_view(), name='featured-events'),
    path('news/featured/', FeaturedNewsView.as_view(), name='featured-news'),
    path('news/latest/', LatestNewsView.as_view(), name='latest-news'),
]