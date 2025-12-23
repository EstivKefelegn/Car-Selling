from rest_framework import generics, permissions, status, viewsets, throttling
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework import filters, status
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.parsers import JSONParser

from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Min, Max, Count
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .models import (
    ElectricCar, CarColor, Manufacturer, CarColorConfiguration,
    EmailSubscriber, CustomerVehicle, ServiceBooking, ServiceReminder, ContactOrder
)
from .serializers import (
    ElectricCarSerializer, ElectricCarListSerializer, ElectricCarDetailSerializer,
    ManufacturerSerializer, CarColorSerializer,
    CarWithColorsSerializer, EmailSubscriberSerializer, 
    PublicEmailSubscriptionSerializer,
    SubscriptionUpdateSerializer,
    UnsubscribeSerializer,
    SalesAssociateSerializer,
    CustomerVehicleSerializer, ServiceBookingSerializer,
    ServiceReminderSerializer, ServiceBookingCreateSerializer,PublicServiceBookingSerializer,
    VehicleCreateSerializer, UserSerializer, ContactOrderCreateSerializer, CarColorListSerializer
)
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


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

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

class CarColorViewSet(viewsets.ModelViewSet):
    queryset = CarColor.objects.all()
    serializer_class = CarColorSerializer  # Default serializer
    parser_classes = [JSONParser]  # Only JSON needed for list input

    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulk_create(self, request):
        """
        Create multiple car colors at once.
        Expects a JSON **list of color objects**.
        """
        colors_data = request.data
        if not isinstance(colors_data, list):
            return Response(
                {"error": "Expected a list of objects."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CarColorSerializer(data=colors_data, many=True)  # ✅ important: many=True
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": f"Successfully created {len(serializer.data)} colors",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class CarColorViewSet(ReadOnlyModelViewSet):
#     """API endpoint for Car Colors with filtering"""
#     queryset = CarColor.objects.all()
#     serializer_class = CarColorSerializer
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter]
#     search_fields = ['name']
    
#     def get_queryset(self):
#         queryset = super().get_queryset()
#         params = self.request.query_params
        
#         # Filter by color type
#         color_type = params.get('color_type')
#         if color_type:
#             queryset = queryset.filter(color_type=color_type)
        
#         # Filter by name
#         name = params.get('name')
#         if name:
#             queryset = queryset.filter(name__icontains=name)
        
#         return queryset

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

class CustomerVehicleViewSet(viewsets.ModelViewSet):
    """ViewSet for customer vehicles"""
    serializer_class = CustomerVehicleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['license_plate', 'vin', 'custom_make', 'custom_model']
    filterset_fields = ['is_neta_car', 'is_eligible_for_10000km_service']
    ordering_fields = ['created_at', 'current_odometer']
    
    def get_queryset(self):
        user = self.request.user
        queryset = CustomerVehicle.objects.filter(customer=user)
        
        # Filter by NETA warranty eligibility
        neta_only = self.request.query_params.get('neta_only')
        if neta_only == 'true':
            queryset = queryset.filter(is_neta_car=True, is_warranty_valid=True)
        
        # Filter by 10,000 KM service eligibility
        km_service = self.request.query_params.get('km_service')
        if km_service == 'true':
            queryset = queryset.filter(is_eligible_for_10000km_service=True)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return VehicleCreateSerializer
        return CustomerVehicleSerializer
    
    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)
    
    @action(detail=False, methods=['get'])
    def neta_eligible(self, request):
        """Get NETA warranty eligible vehicles"""
        vehicles = self.get_queryset().filter(
            is_neta_car=True,
            is_warranty_valid=True
        )
        serializer = self.get_serializer(vehicles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def km_service_eligible(self, request):
        """Get 10,000 KM service eligible vehicles"""
        vehicles = self.get_queryset().filter(
            is_eligible_for_10000km_service=True
        )
        serializer = self.get_serializer(vehicles, many=True)
        return Response(serializer.data)

class ServiceBookingViewSet(viewsets.ModelViewSet):
    """ViewSet for service bookings"""
    serializer_class = ServiceBookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['booking_number', 'vehicle__license_plate', 'vehicle__vin']
    filterset_fields = ['status', 'service_type', 'priority']
    ordering_fields = ['created_at', 'preferred_date', 'scheduled_date']
    
    def get_queryset(self):
        user = self.request.user
        queryset = ServiceBooking.objects.filter(customer=user)
        
        # Filter by upcoming bookings
        upcoming = self.request.query_params.get('upcoming')
        if upcoming == 'true':
            queryset = queryset.filter(
                scheduled_date__gte=timezone.now().date(),
                status__in=['confirmed', 'scheduled']
            )
        
        # Filter by service type
        service_type = self.request.query_params.get('service_type')
        if service_type:
            queryset = queryset.filter(service_type=service_type)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ServiceBookingCreateSerializer
        return ServiceBookingSerializer
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming service bookings"""
        bookings = self.get_queryset().filter(
            scheduled_date__gte=timezone.now().date(),
            status__in=['confirmed', 'scheduled']
        ).order_by('scheduled_date')
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending service bookings"""
        bookings = self.get_queryset().filter(
            status__in=['pending', 'confirmed']
        ).order_by('preferred_date')
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a service booking"""
        booking = self.get_object()
        if booking.status not in ['pending', 'confirmed', 'scheduled']:
            return Response(
                {'error': 'Cannot cancel booking in its current status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'cancelled'
        booking.save()
        return Response({'status': 'Booking cancelled successfully'})

class PublicServiceBookingView(generics.CreateAPIView):
    """Public API for creating service bookings without authentication"""
    serializer_class = PublicServiceBookingSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()

        # Serialize for output using full ServiceBookingSerializer
        output_serializer = ServiceBookingSerializer(booking, context={'request': request})
        headers = self.get_success_headers(serializer.data)
        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class ServiceReminderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for service reminders"""
    serializer_class = ServiceReminderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return ServiceReminder.objects.filter(
            vehicle__customer=user,
            scheduled_send_date__gte=timezone.now().date() - timedelta(days=7),
            is_sent=False
        ).order_by('scheduled_send_date')

class ServiceAvailabilityView(APIView):
    """Check service availability"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        date_str = request.query_params.get('date')
        
        if not date_str:
            return Response(
                {'error': 'Date parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if date is in the past
        if date < timezone.now().date():
            return Response({
                'date': date_str,
                'available_slots': [],
                'message': 'Cannot book for past dates'
            })
        
        # Get booked slots for the day
        booked_slots = ServiceBooking.objects.filter(
            scheduled_date=date,
            status__in=['confirmed', 'scheduled', 'in_progress']
        ).values_list('scheduled_time', flat=True)
        
        # Generate available time slots (9 AM to 5 PM, 1-hour slots)
        available_slots = []
        for hour in range(9, 17):
            time_slot = timezone.datetime.strptime(f'{hour:02d}:00', '%H:%M').time()
            if time_slot not in booked_slots:
                available_slots.append(time_slot.strftime('%H:%M'))
        
        return Response({
            'date': date_str,
            'available_slots': available_slots
        })

class ServiceStatisticsView(APIView):
    """Get service statistics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get vehicle statistics
        total_vehicles = CustomerVehicle.objects.filter(customer=user).count()
        neta_vehicles = CustomerVehicle.objects.filter(customer=user, is_neta_car=True).count()
        service_eligible_vehicles = CustomerVehicle.objects.filter(
            customer=user, 
            is_eligible_for_10000km_service=True
        ).count()
        
        # Get booking statistics
        total_bookings = ServiceBooking.objects.filter(customer=user).count()
        upcoming_bookings = ServiceBooking.objects.filter(
            customer=user,
            scheduled_date__gte=timezone.now().date(),
            status__in=['confirmed', 'scheduled']
        ).count()
        pending_bookings = ServiceBooking.objects.filter(
            customer=user,
            status__in=['pending', 'confirmed']
        ).count()
        
        # Get vehicles needing service
        vehicles_needing_service = CustomerVehicle.objects.filter(
            customer=user,
            is_eligible_for_10000km_service=True
        ).filter(
            Q(next_service_due_km__lte=models.F('current_odometer')) |
            Q(next_service_due_date__lte=timezone.now().date()) |
            Q(last_service_odometer__isnull=True) |
            Q(current_odometer - models.F('last_service_odometer') >= 10000)
        ).count()
        
        return Response({
            'vehicles': {
                'total': total_vehicles,
                'neta': neta_vehicles,
                'service_eligible': service_eligible_vehicles,
                'needing_service': vehicles_needing_service
            },
            'bookings': {
                'total': total_bookings,
                'upcoming': upcoming_bookings,
                'pending': pending_bookings
            }
        })

# Admin views for staff management
class AdminServiceBookingViewSet(viewsets.ModelViewSet):
    """Admin ViewSet for managing all service bookings"""
    serializer_class = ServiceBookingSerializer
    permission_classes = [IsAdminUser]
    queryset = ServiceBooking.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['booking_number', 'customer__email', 'customer__username', 
                    'vehicle__license_plate', 'vehicle__vin']
    filterset_fields = ['status', 'service_type', 'priority', 'service_center']
    ordering_fields = ['created_at', 'scheduled_date', 'preferred_date']
    
    @action(detail=True, methods=['post'])
    def schedule(self, request, pk=None):
        """Schedule a booking"""
        booking = self.get_object()
        date = request.data.get('date')
        time = request.data.get('time')
        service_center_id = request.data.get('service_center')
        
        if not date or not time:
            return Response(
                {'error': 'Date and time are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            scheduled_date = timezone.datetime.strptime(date, '%Y-%m-%d').date()
            scheduled_time = timezone.datetime.strptime(time, '%H:%M').time()
            
            service_center = None
            if service_center_id:
                from company.models import ServiceCenter
                service_center = ServiceCenter.objects.get(id=service_center_id)
            
            booking.schedule_service(
                date=scheduled_date,
                time=scheduled_time,
                scheduled_by=request.user,
                service_center=service_center
            )
            
            serializer = self.get_serializer(booking)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete a service booking"""
        booking = self.get_object()
        final_odometer = request.data.get('final_odometer')
        report = request.data.get('report')
        parts_used = request.data.get('parts_used', [])
        total_cost = request.data.get('total_cost')
        
        if not final_odometer or not report:
            return Response(
                {'error': 'Final odometer and report are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            booking.complete_service(
                technician=request.user,
                final_odometer=final_odometer,
                report=report,
                parts_used=parts_used,
                total_cost=total_cost
            )
            
            serializer = self.get_serializer(booking)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ContactOrderCreateView(generics.CreateAPIView):
    """
    Public endpoint for users to submit contact/order requests
    from the ElectricCar detail page.
    """
    queryset = ContactOrder.objects.all()
    serializer_class = ContactOrderCreateSerializer
    permission_classes = [permissions.AllowAny]

    # Optional: basic anti-spam throttling
    throttle_classes = [throttling.AnonRateThrottle]

    def perform_create(self, serializer):
        serializer.save()
