from rest_framework import generics, permissions, status, viewsets, filters
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework import filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Min, Max, Count
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .models import (
    AboutUs, TeamMember, DealershipPhoto, Event, EventCategory, EventRegistration, News
)
from .serializers import (
    AboutUsSerializer, PublicAboutUsSerializer, AboutUsCreateUpdateSerializer,
    TeamMemberSerializer, DealershipPhotoSerializer, AboutUsBulkSerializer,
    EventListSerializer, EventDetailSerializer,
    EventCategorySerializer, EventRegistrationSerializer, NewsSerializer, NewsListSerializer
)

from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.utils import timezone




# Create your views here

class AboutUsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for AboutUs model (admin only)
    """
    queryset = AboutUs.objects.all()
    serializer_class = AboutUsSerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action in ['create', 'update', 'partial_update']:
            return AboutUsCreateUpdateSerializer
        return AboutUsSerializer
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def public(self, request):
        """Public endpoint for About Us information"""
        about_us = AboutUs.get_active()
        if not about_us:
            return Response({
                'error': 'No active About Us information found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PublicAboutUsSerializer(about_us, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def location(self, request):
        """Get only location information"""
        about_us = AboutUs.get_active()
        if not about_us:
            return Response({
                'error': 'No active location information found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        data = {
            'address': about_us.full_address,
            'coordinates': {
                'latitude': float(about_us.latitude),
                'longitude': float(about_us.longitude)
            },
            'google_maps_url': about_us.google_maps_url,
            'phone': about_us.phone_number,
            'email': about_us.email
        }
        return Response(data)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def bulk_action(self, request):
        """Bulk actions for AboutUs entries"""
        serializer = AboutUsBulkSerializer(data=request.data)
        if serializer.is_valid():
            ids = serializer.validated_data['ids']
            action_type = serializer.validated_data['action']
            
            queryset = AboutUs.objects.filter(id__in=ids)
            
            if action_type == 'activate':
                queryset.update(is_active=True)
                message = f"Activated {queryset.count()} entries"
            elif action_type == 'deactivate':
                queryset.update(is_active=False)
                message = f"Deactivated {queryset.count()} entries"
            elif action_type == 'delete':
                count = queryset.count()
                queryset.delete()
                message = f"Deleted {count} entries"
            
            return Response({'success': True, 'message': message})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeamMemberViewSet(viewsets.ModelViewSet):
    """ViewSet for Team Members"""
    queryset = TeamMember.objects.filter(is_active=True)
    serializer_class = TeamMemberSerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        """Filter by dealership if provided"""
        queryset = super().get_queryset()
        dealership_id = self.request.query_params.get('dealership')
        if dealership_id:
            queryset = queryset.filter(about_us_id=dealership_id)
        return queryset.order_by('display_order', 'full_name')
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def active(self, request):
        """Get active team members for active dealership"""
        about_us = AboutUs.get_active()
        if not about_us:
            return Response([])
        
        team_members = TeamMember.objects.filter(
            about_us=about_us,
            is_active=True
        ).order_by('display_order', 'full_name')
        
        serializer = self.get_serializer(team_members, many=True)
        return Response(serializer.data)


class DealershipPhotoViewSet(viewsets.ModelViewSet):
    """ViewSet for Dealership Photos"""
    queryset = DealershipPhoto.objects.filter(is_active=True)
    serializer_class = DealershipPhotoSerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        """Filter by dealership if provided"""
        queryset = super().get_queryset()
        dealership_id = self.request.query_params.get('dealership')
        if dealership_id:
            queryset = queryset.filter(about_us_id=dealership_id)
        return queryset.order_by('display_order', '-uploaded_at')
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def gallery(self, request):
        """Get active photos for active dealership"""
        about_us = AboutUs.get_active()
        if not about_us:
            return Response([])
        
        photos = DealershipPhoto.objects.filter(
            about_us=about_us,
            is_active=True
        ).order_by('display_order', '-uploaded_at')
        
        serializer = self.get_serializer(photos, many=True)
        return Response(serializer.data)


# Public API Views (no authentication required)
class PublicAboutUsView(generics.RetrieveAPIView):
    """Public view for About Us"""
    permission_classes = [permissions.AllowAny]
    
    def get_object(self):
        about_us = AboutUs.get_active()
        if not about_us:
            raise Http404("No active About Us information found.")
        return about_us
    
    def get_serializer_class(self):
        return PublicAboutUsSerializer


class PublicTeamMembersView(generics.ListAPIView):
    """Public view for team members"""
    permission_classes = [permissions.AllowAny]
    serializer_class = TeamMemberSerializer
    
    def get_queryset(self):
        about_us = AboutUs.get_active()
        if not about_us:
            return TeamMember.objects.none()
        
        return TeamMember.objects.filter(
            about_us=about_us,
            is_active=True
        ).order_by('display_order', 'full_name')


class PublicDealershipGalleryView(generics.ListAPIView):
    """Public view for dealership gallery"""
    permission_classes = [permissions.AllowAny]
    serializer_class = DealershipPhotoSerializer
    
    def get_queryset(self):
        about_us = AboutUs.get_active()
        if not about_us:
            return DealershipPhoto.objects.none()
        
        return DealershipPhoto.objects.filter(
            about_us=about_us,
            is_active=True
        ).order_by('display_order', '-uploaded_at')        


class EventCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EventCategory.objects.all()
    serializer_class = EventCategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

class EventViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EventListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event_type', 'category', 'is_virtual', 'is_featured', 'status']
    search_fields = ['title', 'description', 'venue_name', 'city', 'country']
    ordering_fields = ['start_date', 'title', 'created_at', 'views']
    ordering = ['start_date']
    lookup_field = 'slug'
    
    def get_queryset(self):
        queryset = Event.objects.exclude(status='draft')
        
        # Filter by upcoming/ongoing/completed
        status_filter = self.request.query_params.get('status_filter', None)
        if status_filter == 'upcoming':
            queryset = queryset.filter(start_date__gt=timezone.now())
        elif status_filter == 'ongoing':
            queryset = queryset.filter(
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now()
            )
        elif status_filter == 'past':
            queryset = queryset.filter(end_date__lt=timezone.now())
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EventDetailSerializer
        return EventListSerializer
    
    @action(detail=True, methods=['post'])
    def register(self, request, slug=None):
        """Register for an event"""
        event = self.get_object()
        serializer = EventRegistrationSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            registration = serializer.save(
                event=event,
                user=request.user if request.user.is_authenticated else None
            )
            return Response(
                EventRegistrationSerializer(registration).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def increment_views(self, request, slug=None):
        """Increment event view count"""
        event = self.get_object()
        event.increment_views()
        return Response({'views': event.views})

class EventRegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = EventRegistrationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return EventRegistration.objects.all()
        return EventRegistration.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UpcomingEventsView(generics.ListAPIView):
    """Get upcoming events (next 30 days)"""
    serializer_class = EventListSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return Event.objects.filter(
            status__in=['upcoming', 'ongoing'],
            start_date__lte=timezone.now() + timezone.timedelta(days=30)
        ).order_by('start_date')[:10]

class FeaturedEventsView(generics.ListAPIView):
    """Get featured events"""
    serializer_class = EventListSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return Event.objects.filter(
            is_featured=True,
            status__in=['upcoming', 'ongoing']
        ).order_by('start_date')

class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Simple news API endpoint.
    """
    serializer_class = NewsListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_featured']
    search_fields = ['title', 'description', 'content']
    ordering_fields = ['published_at', 'created_at']
    ordering = ['-published_at']
    lookup_field = 'slug'
    
    def get_queryset(self):
        queryset = News.objects.filter(status='published')
        
        # Filter by featured if requested
        is_featured = self.request.query_params.get('is_featured', None)
        if is_featured == 'true':
            queryset = queryset.filter(is_featured=True)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return NewsSerializer
        return NewsListSerializer

class FeaturedNewsView(generics.ListAPIView):
    """
    Get featured news articles.
    """
    serializer_class = NewsListSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return News.objects.filter(
            status='published',
            is_featured=True
        ).order_by('-published_at')[:6]

class LatestNewsView(generics.ListAPIView):
    """
    Get latest news articles.
    """
    serializer_class = NewsListSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        limit = self.request.query_params.get('limit', 10)
        return News.objects.filter(
            status='published'
        ).order_by('-published_at')[:int(limit)]