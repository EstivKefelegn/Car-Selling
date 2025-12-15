from rest_framework import generics, permissions, status, viewsets
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
    ElectricCar, CarColor, Manufacturer, CarColorConfiguration,
    EmailSubscriber, AboutUs, TeamMember, DealershipPhoto
)
from .serializers import (
    ElectricCarSerializer, ElectricCarListSerializer, ElectricCarDetailSerializer,
    ManufacturerSerializer, CarColorSerializer,
    CarWithColorsSerializer, EmailSubscriberSerializer, 
    PublicEmailSubscriptionSerializer,
    SubscriptionUpdateSerializer,
    UnsubscribeSerializer,
    SalesAssociateSerializer,
    AboutUsSerializer, PublicAboutUsSerializer, AboutUsCreateUpdateSerializer,
    TeamMemberSerializer, DealershipPhotoSerializer, AboutUsBulkSerializer

)


class ElectricCarViewSet(ModelViewSet):
    """
    API endpoint for Electric Cars with comprehensive filtering.
    
    Filter:
    - /api/electric-cars/?manufacturer=Tesla
    - /api/electric-cars/?model_name=Model 3
    - /api/electric-cars/?min_price=1000000&max_price=5000000
    - /api/electric-cars/?min_year=2020&max_year=2024
    - /api/electric-cars/?category=sedan
    - /api/electric-cars/?exterior_color=Red&interior_color=Black
    - /api/electric-cars/?featured=true
    - /api/electric-cars/?search=Tesla
    - /api/electric-cars/?ordering=-base_price
    """
    
    queryset = ElectricCar.objects.all().select_related('manufacturer')
    serializer_class = ElectricCarSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Search fields
    search_fields = [
        'model_name', 'variant', 'manufacturer__name',
        'description', 'key_features'
    ]
    
    # Ordering fields
    ordering_fields = [
        'model_year', 'base_price', 'range_wltp', 'battery_capacity',
        'acceleration_0_100', 'motor_power', 'created_at'
    ]
    ordering = ['-created_at']  # Default: newest first
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'list':
            return ElectricCarListSerializer
        elif self.action == 'retrieve':
            return ElectricCarDetailSerializer
        return ElectricCarSerializer
    
    def get_queryset(self):
        """
        Comprehensive filtering for Electric Cars.
        Supports filtering by:
        - Manufacturer (name or ID)
        - Model name
        - Year range
        - Price range
        - Range (WLTP) range
        - Battery capacity range
        - Category
        - Status
        - Features (V2L, V2G, etc.)
        - Colors
        """
        queryset = super().get_queryset()
        params = self.request.query_params
        
        # Manufacturer filtering
        manufacturer = params.get('manufacturer')
        manufacturer_id = params.get('manufacturer_id')
        
        if manufacturer:
            queryset = queryset.filter(manufacturer__name__icontains=manufacturer)
        if manufacturer_id:
            queryset = queryset.filter(manufacturer__id=manufacturer_id)
        
        # Model filtering
        model_name = params.get('model_name')
        if model_name:
            queryset = queryset.filter(model_name__icontains=model_name)
        
        variant = params.get('variant')
        if variant:
            queryset = queryset.filter(variant__icontains=variant)
        
        # Year range filtering
        min_year = params.get('min_year')
        max_year = params.get('max_year')
        if min_year:
            queryset = queryset.filter(model_year__gte=min_year)
        if max_year:
            queryset = queryset.filter(model_year__lte=max_year)
        
        # Price range filtering
        min_price = params.get('min_price')
        max_price = params.get('max_price')
        if min_price:
            queryset = queryset.filter(base_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(base_price__lte=max_price)
        
        # Range (WLTP) filtering
        min_range = params.get('min_range')
        max_range = params.get('max_range')
        if min_range:
            queryset = queryset.filter(range_wltp__gte=min_range)
        if max_range:
            queryset = queryset.filter(range_wltp__lte=max_range)
        
        # Battery capacity filtering
        min_battery = params.get('min_battery')
        max_battery = params.get('max_battery')
        if min_battery:
            queryset = queryset.filter(battery_capacity__gte=min_battery)
        if max_battery:
            queryset = queryset.filter(battery_capacity__lte=max_battery)
        
        # Acceleration filtering
        min_acceleration = params.get('min_acceleration')
        max_acceleration = params.get('max_acceleration')
        if min_acceleration:
            queryset = queryset.filter(acceleration_0_100__lte=min_acceleration)
        if max_acceleration:
            queryset = queryset.filter(acceleration_0_100__gte=max_acceleration)
        
        # Category filtering
        category = params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Multiple categories
        categories = params.get('categories')
        if categories:
            category_list = categories.split(',')
            queryset = queryset.filter(category__in=category_list)
        
        # Status filtering
        status = params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Multiple statuses
        statuses = params.get('statuses')
        if statuses:
            status_list = statuses.split(',')
            queryset = queryset.filter(status__in=status_list)
        
        # Battery type filtering
        battery_type = params.get('battery_type')
        if battery_type:
            queryset = queryset.filter(battery_type=battery_type)
        
        # Multiple battery types
        battery_types = params.get('battery_types')
        if battery_types:
            battery_list = battery_types.split(',')
            queryset = queryset.filter(battery_type__in=battery_list)
        
        # Drive type filtering
        drive_type = params.get('drive_type')
        if drive_type:
            queryset = queryset.filter(drive_type=drive_type)
        
        # Charging type filtering
        charging_type = params.get('charging_type')
        if charging_type:
            queryset = queryset.filter(charging_type=charging_type)
        
        # Boolean feature filters
        featured = params.get('featured')
        if featured is not None:
            queryset = queryset.filter(featured=featured.lower() == 'true')
        
        has_v2l = params.get('has_v2l')
        if has_v2l is not None:
            queryset = queryset.filter(has_v2l=has_v2l.lower() == 'true')
        
        has_v2g = params.get('has_v2g')
        if has_v2g is not None:
            queryset = queryset.filter(has_v2g=has_v2g.lower() == 'true')
        
        has_heat_pump = params.get('has_heat_pump')
        if has_heat_pump is not None:
            queryset = queryset.filter(has_heat_pump=has_heat_pump.lower() == 'true')
        
        tax_incentive = params.get('tax_incentive')
        if tax_incentive is not None:
            queryset = queryset.filter(tax_incentive=tax_incentive.lower() == 'true')
        
        # Color filtering
        exterior_color = params.get('exterior_color')
        if exterior_color:
            queryset = queryset.filter(available_exterior_colors__name__icontains=exterior_color)
        
        interior_color = params.get('interior_color')
        if interior_color:
            queryset = queryset.filter(available_interior_colors__name__icontains=interior_color)
        
        # Color ID filtering
        exterior_color_id = params.get('exterior_color_id')
        if exterior_color_id:
            queryset = queryset.filter(available_exterior_colors__id=exterior_color_id)
        
        interior_color_id = params.get('interior_color_id')
        if interior_color_id:
            queryset = queryset.filter(available_interior_colors__id=interior_color_id)
        
        # Motor power filtering
        min_motor_power = params.get('min_motor_power')
        max_motor_power = params.get('max_motor_power')
        if min_motor_power:
            queryset = queryset.filter(motor_power__gte=min_motor_power)
        if max_motor_power:
            queryset = queryset.filter(motor_power__lte=max_motor_power)
        
        # Top speed filtering
        min_top_speed = params.get('min_top_speed')
        if min_top_speed:
            queryset = queryset.filter(top_speed__gte=min_top_speed)
        
        # Charging speed filtering
        min_charging_speed = params.get('min_charging_speed')
        if min_charging_speed:
            queryset = queryset.filter(max_dc_charging__gte=min_charging_speed)
        
        # Seating capacity filtering
        min_seats = params.get('min_seats')
        if min_seats:
            queryset = queryset.filter(seating_capacity__gte=min_seats)
        
        max_seats = params.get('max_seats')
        if max_seats:
            queryset = queryset.filter(seating_capacity__lte=max_seats)
        
        return queryset.distinct()
    
    @action(detail=False, methods=['GET'])
    def filter_options(self, request):
        """
        Get available filter options for frontend filtering UI
        Returns min/max values and distinct choices
        """
        queryset = self.get_queryset()
        
        # Get ranges
        price_range = queryset.aggregate(
            min_price=Min('base_price'),
            max_price=Max('base_price')
        )
        
        year_range = queryset.aggregate(
            min_year=Min('model_year'),
            max_year=Max('model_year')
        )
        
        range_values = queryset.aggregate(
            min_range=Min('range_wltp'),
            max_range=Max('range_wltp')
        )
        
        battery_range = queryset.aggregate(
            min_battery=Min('battery_capacity'),
            max_battery=Max('battery_capacity')
        )
        
        # Get manufacturers with cars
        manufacturers = Manufacturer.objects.annotate(
            car_count=Count('electric_cars')
        ).filter(car_count__gt=0).values('id', 'name')
        
        # Get distinct categories
        categories = queryset.values_list('category', flat=True).distinct()
        category_choices = []
        for category in categories:
            display = dict(ElectricCar.CATEGORY_CHOICES).get(category, category)
            category_choices.append({'value': category, 'display': display})
        
        # Get status options
        status_options = []
        for value, display in ElectricCar.STATUS_CHOICES:
            count = queryset.filter(status=value).count()
            if count > 0:
                status_options.append({
                    'value': value,
                    'display': display,
                    'count': count
                })
        
        # Get available colors
        exterior_colors = CarColor.objects.filter(
            color_type='exterior',
            available_exterior_cars__isnull=False
        ).distinct().values('id', 'name')
        
        interior_colors = CarColor.objects.filter(
            color_type='interior',
            available_interior_cars__isnull=False
        ).distinct().values('id', 'name')
        
        data = {
            'price_range': {
                'min': float(price_range['min_price'] or 0),
                'max': float(price_range['max_price'] or 0)
            },
            'year_range': {
                'min': year_range['min_year'] or 2020,
                'max': year_range['max_year'] or 2024
            },
            'range_values': {
                'min': range_values['min_range'] or 200,
                'max': range_values['max_range'] or 800
            },
            'battery_range': {
                'min': float(battery_range['min_battery'] or 0),
                'max': float(battery_range['max_battery'] or 0)
            },
            'manufacturers': list(manufacturers),
            'categories': category_choices,
            'status_options': status_options,
            'exterior_colors': list(exterior_colors),
            'interior_colors': list(interior_colors),
            'battery_types': [
                {'value': value, 'display': display}
                for value, display in ElectricCar.BATTERY_TYPE_CHOICES
            ],
            'drive_types': [
                {'value': value, 'display': display}
                for value, display in ElectricCar.DRIVE_TYPE_CHOICES
            ],
            'charging_types': [
                {'value': value, 'display': display}
                for value, display in ElectricCar.CHARGING_TYPE_CHOICES
            ],
        }
        
        return Response(data)
    
    @action(detail=False, methods=['GET'])
    def featured(self, request):
        """Get featured electric cars"""
        queryset = self.get_queryset().filter(featured=True, status='available')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def available(self, request):
        """Get available cars for sale"""
        queryset = self.get_queryset().filter(
            status__in=['available', 'pre_order', 'coming_soon']
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['GET'])
    def color_configurations(self, request, pk=None):
        """Get all color configurations for a specific car"""
        car = self.get_object()
        configs = car.color_configurations.filter(is_available=True)
        serializer = CarColorConfigurationSerializer(configs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['POST'])
    def request_test_drive(self, request, pk=None):
        """Create a test drive request for this car"""
        from .serializers import TestDriveRequestSerializer
        car = self.get_object()
        
        data = request.data.copy()
        data['car'] = car.id
        
        serializer = TestDriveRequestSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ManufacturerViewSet(ModelViewSet):
    """API endpoint for Manufacturers with filtering and create support"""
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'country']

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params
        
        # Filter by country
        country = params.get('country')
        if country:
            queryset = queryset.filter(country__icontains=country)
        
        # Filter by EV only status
        is_ev_only = params.get('is_ev_only')
        if is_ev_only is not None:
            queryset = queryset.filter(is_ev_only=is_ev_only.lower() == 'true')
        
        # Filter by name
        name = params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)
        
        return queryset

    @action(detail=True, methods=['GET'])
    def cars(self, request, pk=None):
        """Get all cars for a specific manufacturer"""
        manufacturer = self.get_object()
        
        # Get all query parameters
        params = request.query_params
        
        # Start with manufacturer's cars
        cars = manufacturer.electric_cars.all()
        
        # Apply filters
        min_year = params.get('min_year')
        max_year = params.get('max_year')
        if min_year:
            cars = cars.filter(model_year__gte=min_year)
        if max_year:
            cars = cars.filter(model_year__lte=max_year)
        
        min_price = params.get('min_price')
        max_price = params.get('max_price')
        if min_price:
            cars = cars.filter(base_price__gte=min_price)
        if max_price:
            cars = cars.filter(base_price__lte=max_price)
        
        status = params.get('status')
        if status:
            cars = cars.filter(status=status)
        
        category = params.get('category')
        if category:
            cars = cars.filter(category=category)
        
        ordering = params.get('ordering')
        if ordering:
            cars = cars.order_by(ordering)
        else:
            cars = cars.order_by('-model_year')
        
        page = self.paginate_queryset(cars)
        if page is not None:
            serializer = ElectricCarListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ElectricCarListSerializer(cars, many=True, context={'request': request})
        return Response(serializer.data)

class CarColorViewSet(ReadOnlyModelViewSet):
    """API endpoint for Car Colors with filtering"""
    queryset = CarColor.objects.all()
    serializer_class = CarColorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params
        
        # Filter by color type
        color_type = params.get('color_type')
        if color_type:
            queryset = queryset.filter(color_type=color_type)
        
        # Filter by name
        name = params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)
        
        return queryset



class SubscribeView(APIView):
    """
    API endpoint for subscribing to email list
    This is public and doesn't require authentication
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PublicEmailSubscriptionSerializer(data=request.data)
        
        if serializer.is_valid():
            subscriber = serializer.save()
            
            # You can send a welcome email here if needed
            # send_welcome_email(subscriber.email)
            
            return Response({
                'success': True,
                'message': 'Successfully subscribed to our mailing list!',
                'data': {
                    'id': subscriber.id,
                    'email': subscriber.email,
                    'first_name': subscriber.first_name,
                    'last_name': subscriber.last_name,
                    'subscribed_at': subscriber.subscribed_at
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UnsubscribeView(APIView):
    """API endpoint for unsubscribing"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UnsubscribeSerializer(data=request.data)
        
        if serializer.is_valid():
            result = serializer.unsubscribe()
            return Response(result, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionPreferencesView(APIView):
    """API endpoint for managing subscription preferences"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        email = request.query_params.get('email')
        
        if not email:
            return Response({
                'success': False,
                'message': 'Email parameter is required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            subscriber = EmailSubscriber.objects.get(email=email.lower())
            serializer = EmailSubscriberSerializer(subscriber)
            return Response({
                'success': True,
                'data': serializer.data
            })
        except EmailSubscriber.DoesNotExist:
            return Response({
                'success': False,
                'message': 'No subscription found with this email.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def patch(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({
                'success': False,
                'message': 'Email is required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            subscriber = EmailSubscriber.objects.get(email=email.lower())
            serializer = SubscriptionUpdateSerializer(
                subscriber, 
                data=request.data,
                partial=True
            )
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Preferences updated successfully.',
                    'data': serializer.data
                })
            
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except EmailSubscriber.DoesNotExist:
            return Response({
                'success': False,
                'message': 'No subscription found with this email.'
            }, status=status.HTTP_404_NOT_FOUND)


class SalesAssociateListView(APIView):
    """Get list of sales associates for dropdown in React"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        # Get all staff users who can be sales associates
        sales_associates = User.objects.filter(
            is_staff=True,
            is_active=True
        ).order_by('first_name', 'last_name')
        
        serializer = SalesAssociateSerializer(sales_associates, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })


class EmailSubscriberViewSet(viewsets.ModelViewSet):
    """Admin viewset for managing email subscribers"""
    queryset = EmailSubscriber.objects.all()
    serializer_class = EmailSubscriberSerializer
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active subscribers"""
        active_subscribers = EmailSubscriber.get_active_subscribers()
        serializer = self.get_serializer(active_subscribers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get subscription statistics"""
        total = EmailSubscriber.objects.count()
        active = EmailSubscriber.objects.filter(
            subscription_status=EmailSubscriber.SubscriptionStatus.ACTIVE
        ).count()
        with_alerts = EmailSubscriber.objects.filter(
            receive_inventory_alerts=True
        ).count()
        
        return Response({
            'total_subscribers': total,
            'active_subscribers': active,
            'with_inventory_alerts': with_alerts
        })


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