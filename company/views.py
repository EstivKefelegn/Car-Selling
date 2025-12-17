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
    AboutUs, TeamMember, DealershipPhoto, Event, EventCategory, EventRegistration, News, FinanceInformationPage, FinanceFAQ, FinanceOffer,
    FinanceCalculator, FinanceDocument, FinancePartner, ServiceCategory, Service, ServicePackage,
    ServiceFAQ, ServiceTestimonial, ServiceCenter
)
from .serializers import (
    AboutUsSerializer, PublicAboutUsSerializer, AboutUsCreateUpdateSerializer,
    TeamMemberSerializer, DealershipPhotoSerializer, AboutUsBulkSerializer,
    EventListSerializer, EventDetailSerializer,
    EventCategorySerializer, EventRegistrationSerializer, NewsSerializer, NewsListSerializer,
    FinanceInformationPageSerializer, FinanceFAQSerializer,
    FinanceOfferSerializer, FinanceCalculatorSerializer,
    FinanceDocumentSerializer, FinancePartnerSerializer,
    LoanCalculationSerializer, LoanCalculationResultSerializer,
    CarFinanceOfferSerializer, ServiceCategorySerializer, ServiceSerializer,
    ServicePackageSerializer, ServiceFAQSerializer,
    ServiceTestimonialSerializer, ServiceCenterSerializer
)

from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.utils import timezone
from datetime import date
from etop_backend.models import ElectricCar




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

# finance/api/views.py


class FinanceInformationPageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FinanceInformationPage.objects.filter(is_active=True)
    serializer_class = FinanceInformationPageSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        slug = self.request.query_params.get('slug', None)
        if slug:
            queryset = queryset.filter(slug=slug)
        return queryset
    
    @action(detail=False, methods=['get'])
    def homepage(self, request):
        """Get the main finance homepage"""
        page = get_object_or_404(FinanceInformationPage, slug='home', is_active=True)
        serializer = self.get_serializer(page)
        return Response(serializer.data)

class FinanceFAQViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FinanceFAQ.objects.filter(is_active=True)
    serializer_class = FinanceFAQSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        return queryset
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get all FAQ categories"""
        categories = FinanceFAQ.CATEGORY_CHOICES
        return Response([{'value': c[0], 'label': c[1]} for c in categories])


class FinanceOfferViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FinanceOffer.objects.filter(is_active=True)
    serializer_class = FinanceOfferSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        today = date.today()
        
        # Filter by current offers by default
        current_only = self.request.query_params.get('current_only', 'true').lower() == 'true'
        if current_only:
            queryset = queryset.filter(
                valid_from__lte=today,
                valid_until__gte=today
            )
        
        # Filter by offer type
        offer_type = self.request.query_params.get('offer_type', None)
        if offer_type:
            queryset = queryset.filter(offer_type=offer_type)
        
        # Filter by featured
        featured = self.request.query_params.get('featured', None)
        if featured:
            queryset = queryset.filter(display_priority=1)
        
        return queryset.order_by('display_priority', '-valid_from')
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current active offers only"""
        today = date.today()
        offers = self.get_queryset().filter(
            valid_from__lte=today,
            valid_until__gte=today
        ).order_by('display_priority', '-valid_from')
        
        serializer = self.get_serializer(offers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def for_car(self, request):
        """Get offers applicable to a specific electric car"""
        car_id = request.query_params.get('car_id')
        if not car_id:
            return Response(
                {'error': 'car_id parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            car = ElectricCar.objects.select_related('manufacturer').get(id=car_id)
            
            # Get offers based on car price, category, etc.
            base_price = float(car.base_price)
            
            # Filter offers based on car characteristics
            offers = self.get_queryset().filter(
                Q(min_credit_score__isnull=True) | Q(min_credit_score__lte=700),
                # Additional logic can be added here based on car price, category, etc.
            )
            
            # Calculate estimated monthly payment for this car
            recommended_offer = offers.first()
            estimated_payment = None
            
            if recommended_offer and recommended_offer.apr_rate:
                # Calculate loan amount (car price minus typical down payment)
                down_payment_percent = recommended_offer.down_payment_percent or 10.0
                down_payment_amount = base_price * (down_payment_percent / 100)
                loan_amount = base_price - down_payment_amount
                
                # Get term (default to 60 months if not specified)
                term = recommended_offer.term_months or 60
                monthly_rate = float(recommended_offer.apr_rate) / 100 / 12
                
                # Calculate monthly payment
                if monthly_rate > 0:
                    monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** term) / ((1 + monthly_rate) ** term - 1)
                else:
                    monthly_payment = loan_amount / term
                
                estimated_payment = round(monthly_payment, 2)
            
            # Prepare car data
            car_data = {
                'car_id': car.id,
                'car_name': f"{car.manufacturer.name} {car.model_name}",
                'car_display_name': car.display_name,
                'manufacturer_name': car.manufacturer.name,
                'model_name': car.model_name,
                'variant': car.variant or '',
                'model_year': car.model_year,
                'price': car.base_price,
                'main_image': car.main_image.url if car.main_image else None,
                'category': car.category,
                'status': car.status,
                'range_wltp': car.range_wltp,
            }
            
            # Prepare response
            data = {
                **car_data,
                'special_offers': FinanceOfferSerializer(offers[:5], many=True).data,
                'estimated_monthly_payment': estimated_payment,
                'recommended_offer': FinanceOfferSerializer(recommended_offer).data if recommended_offer else None,
                'car_details': {
                    'battery_capacity': float(car.battery_capacity),
                    'acceleration_0_100': float(car.acceleration_0_100),
                    'top_speed': car.top_speed,
                    'seating_capacity': car.seating_capacity,
                    'drive_type': car.get_drive_type_display(),
                    'charging_time_10_80': car.charging_time_10_80,
                    'warranty_years': car.battery_warranty_years,
                    'warranty_km': car.battery_warranty_km,
                }
            }
            
            return Response(data)
            
        except ElectricCar.DoesNotExist:
            return Response(
                {'error': 'Electric car not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def for_category(self, request):
        """Get offers for cars in a specific category"""
        category = request.query_params.get('category')
        max_price = request.query_params.get('max_price')
        
        if not category:
            return Response(
                {'error': 'category parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get cars in this category
        cars = ElectricCar.objects.filter(
            category=category,
            is_available_for_sale=True
        )
        
        if max_price:
            cars = cars.filter(base_price__lte=max_price)
        
        # Get offers for these cars
        offers = self.get_queryset()
        
        # Find best offer for each car
        results = []
        for car in cars[:10]:  # Limit to 10 cars
            # Find suitable offers for this car's price range
            suitable_offers = offers.filter(
                min_loan_amount__lte=car.base_price,
                max_loan_amount__gte=car.base_price
            )[:3]
            
            if suitable_offers:
                best_offer = suitable_offers.first()
                
                # Calculate estimated payment
                loan_amount = float(car.base_price) * 0.9  # 10% down
                term = best_offer.term_months or 60
                monthly_rate = float(best_offer.apr_rate or 5.99) / 100 / 12
                
                if monthly_rate > 0:
                    monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** term) / ((1 + monthly_rate) ** term - 1)
                else:
                    monthly_payment = loan_amount / term
                
                results.append({
                    'car': {
                        'id': car.id,
                        'name': car.display_name,
                        'price': car.base_price,
                        'image': request.build_absolute_uri(car.main_image.url) if car.main_image else None,
                        'range': car.range_wltp,
                        'acceleration': float(car.acceleration_0_100),
                    },
                    'best_offer': FinanceOfferSerializer(best_offer).data,
                    'estimated_monthly_payment': round(monthly_payment, 2),
                    'suitable_offers': FinanceOfferSerializer(suitable_offers, many=True).data
                })
        
        return Response({
            'category': category,
            'category_display': dict(ElectricCar.CATEGORY_CHOICES).get(category, category),
            'total_cars': cars.count(),
            'financing_options': results
        })

class FinanceCalculatorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FinanceCalculator.objects.filter(is_active=True)
    serializer_class = FinanceCalculatorSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        calculator_type = self.request.query_params.get('type', None)
        if calculator_type:
            queryset = queryset.filter(calculator_type=calculator_type)
        return queryset
    
    @action(detail=False, methods=['post'])
    def calculate_loan(self, request):
        """Calculate loan payment"""
        serializer = LoanCalculationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Extract values
        car_price = float(data['car_price'])
        down_payment = float(data['down_payment'])
        interest_rate = float(data['interest_rate'])
        term_months = int(data['term_months'])
        trade_in_value = float(data.get('trade_in_value', 0))
        sales_tax = float(data.get('sales_tax', 0))
        
        # Calculate total amount financed
        tax_amount = (car_price - trade_in_value) * (sales_tax / 100)
        total_financed = car_price + tax_amount - down_payment - trade_in_value
        
        if total_financed <= 0:
            return Response({
                'success': True,
                'monthly_payment': 0,
                'total_loan_amount': 0,
                'total_interest': 0,
                'total_cost': down_payment + trade_in_value,
                'down_payment': down_payment
            })
        
        # Calculate monthly payment
        monthly_rate = interest_rate / 100 / 12
        
        if monthly_rate > 0:
            monthly_payment = total_financed * (monthly_rate * (1 + monthly_rate) ** term_months) / ((1 + monthly_rate) ** term_months - 1)
        else:
            monthly_payment = total_financed / term_months
        
        # Calculate totals
        total_payment = monthly_payment * term_months
        total_interest = total_payment - total_financed
        total_cost = total_payment + down_payment + trade_in_value
        
        # Generate amortization schedule
        amortization_schedule = []
        remaining_balance = total_financed
        
        for month in range(1, term_months + 1):
            interest_payment = remaining_balance * monthly_rate
            principal_payment = monthly_payment - interest_payment
            remaining_balance -= principal_payment
            
            amortization_schedule.append({
                'month': month,
                'payment': round(monthly_payment, 2),
                'principal': round(principal_payment, 2),
                'interest': round(interest_payment, 2),
                'remaining_balance': round(max(0, remaining_balance), 2)
            })
        
        result = {
            'success': True,
            'monthly_payment': round(monthly_payment, 2),
            'total_loan_amount': round(total_financed, 2),
            'total_interest': round(total_interest, 2),
            'total_cost': round(total_cost, 2),
            'down_payment': down_payment,
            'amortization_schedule': amortization_schedule
        }
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def estimate_affordability(self, request):
        """Estimate what car price you can afford based on income"""
        monthly_income = float(request.query_params.get('monthly_income', 0))
        monthly_debts = float(request.query_params.get('monthly_debts', 0))
        down_payment = float(request.query_params.get('down_payment', 0))
        term_months = int(request.query_params.get('term_months', 60))
        interest_rate = float(request.query_params.get('interest_rate', 5.99))
        
        # Common rule: car payment should not exceed 10-15% of monthly income
        max_monthly_payment = (monthly_income - monthly_debts) * 0.15
        
        if max_monthly_payment <= 0:
            return Response({
                'affordable_price': 0,
                'max_monthly_payment': 0,
                'message': 'Income too low after debts'
            })
        
        # Calculate maximum car price
        monthly_rate = interest_rate / 100 / 12
        
        if monthly_rate > 0:
            loan_amount = max_monthly_payment * ((1 + monthly_rate) ** term_months - 1) / (monthly_rate * (1 + monthly_rate) ** term_months)
        else:
            loan_amount = max_monthly_payment * term_months
        
        affordable_price = loan_amount + down_payment
        
        return Response({
            'affordable_price': round(affordable_price, 2),
            'max_monthly_payment': round(max_monthly_payment, 2),
            'recommended_price': round(affordable_price * 0.9, 2),  # Conservative estimate
            'loan_amount': round(loan_amount, 2),
            'down_payment': down_payment
        })

class FinanceDocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FinanceDocument.objects.filter(is_active=True)
    serializer_class = FinanceDocumentSerializer
    permission_classes = [AllowAny]

class FinancePartnerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FinancePartner.objects.filter(is_active=True)
    serializer_class = FinancePartnerSerializer
    permission_classes = [AllowAny]


class FinanceComparisonViewSet(viewsets.GenericViewSet):
    """Viewset for comparing finance options across multiple cars"""
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def compare_cars(self, request):
        """Compare finance options for multiple cars"""
        car_ids = request.query_params.get('car_ids', '')
        
        if not car_ids:
            return Response(
                {'error': 'car_ids parameter is required (comma-separated)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            car_id_list = [int(id.strip()) for id in car_ids.split(',') if id.strip()]
            cars = ElectricCar.objects.filter(id__in=car_id_list).select_related('manufacturer')
            
            if not cars:
                return Response(
                    {'error': 'No cars found with the provided IDs'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get all active offers
            offers = FinanceOffer.objects.filter(is_active=True)
            
            comparison_data = []
            for car in cars:
                # Find suitable offers for this car
                suitable_offers = offers.filter(
                    min_loan_amount__lte=car.base_price,
                    max_loan_amount__gte=car.base_price
                )[:3]
                
                car_offers = []
                for offer in suitable_offers:
                    # Calculate payment for each offer
                    down_payment_percent = offer.down_payment_percent or 10.0
                    down_payment = float(car.base_price) * (down_payment_percent / 100)
                    loan_amount = float(car.base_price) - down_payment
                    term = offer.term_months or 60
                    monthly_rate = float(offer.apr_rate or 5.99) / 100 / 12
                    
                    if monthly_rate > 0:
                        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** term) / ((1 + monthly_rate) ** term - 1)
                    else:
                        monthly_payment = loan_amount / term
                    
                    total_interest = (monthly_payment * term) - loan_amount
                    
                    car_offers.append({
                        'offer': FinanceOfferSerializer(offer).data,
                        'down_payment': round(down_payment, 2),
                        'monthly_payment': round(monthly_payment, 2),
                        'total_interest': round(total_interest, 2),
                        'total_cost': round(monthly_payment * term + down_payment, 2)
                    })
                
                comparison_data.append({
                    'car': {
                        'id': car.id,
                        'name': car.display_name,
                        'manufacturer': car.manufacturer.name,
                        'model': car.model_name,
                        'variant': car.variant,
                        'year': car.model_year,
                        'price': car.base_price,
                        'image': request.build_absolute_uri(car.main_image.url) if car.main_image else None,
                        'range': car.range_wltp,
                        'acceleration': float(car.acceleration_0_100),
                        'category': car.get_category_display(),
                        'status': car.get_status_display(),
                    },
                    'finance_options': car_offers,
                    'recommended_option': car_offers[0] if car_offers else None
                })
            
            # Find best overall option
            if comparison_data:
                best_option = min(
                    comparison_data,
                    key=lambda x: x['recommended_option']['monthly_payment'] 
                    if x['recommended_option'] else float('inf')
                )
            else:
                best_option = None
            
            return Response({
                'comparison': comparison_data,
                'best_overall_option': best_option,
                'total_cars': len(comparison_data)
            })
            
        except ValueError:
            return Response(
                {'error': 'Invalid car_ids format. Use comma-separated numbers.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def calculate_bulk(self, request):
        """Calculate finance for multiple cars at once"""
        data = request.data
        if not isinstance(data, list):
            return Response(
                {'error': 'Expected a list of car finance calculations'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = []
        for item in data:
            try:
                car_id = item.get('car_id')
                down_payment = float(item.get('down_payment', 0))
                term_months = int(item.get('term_months', 60))
                interest_rate = float(item.get('interest_rate', 5.99))
                
                car = ElectricCar.objects.get(id=car_id)
                car_price = float(car.base_price)
                
                # Calculate
                loan_amount = car_price - down_payment
                monthly_rate = interest_rate / 100 / 12
                
                if monthly_rate > 0:
                    monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** term_months) / ((1 + monthly_rate) ** term_months - 1)
                else:
                    monthly_payment = loan_amount / term_months
                
                total_interest = (monthly_payment * term_months) - loan_amount
                total_cost = monthly_payment * term_months + down_payment
                
                results.append({
                    'car_id': car_id,
                    'car_name': car.display_name,
                    'car_price': car_price,
                    'down_payment': down_payment,
                    'term_months': term_months,
                    'interest_rate': interest_rate,
                    'monthly_payment': round(monthly_payment, 2),
                    'total_interest': round(total_interest, 2),
                    'total_cost': round(total_cost, 2),
                    'affordability_score': self._calculate_affordability_score(monthly_payment, car_price)
                })
                
            except ElectricCar.DoesNotExist:
                results.append({
                    'car_id': car_id,
                    'error': 'Car not found'
                })
            except Exception as e:
                results.append({
                    'car_id': car_id,
                    'error': str(e)
                })
        
        return Response({
            'calculations': results,
            'summary': {
                'total_cars': len(results),
                'successful': len([r for r in results if 'error' not in r]),
                'average_monthly_payment': self._calculate_average([r.get('monthly_payment') for r in results if 'monthly_payment' in r])
            }
        })
    
    def _calculate_affordability_score(self, monthly_payment, car_price):
        """Calculate affordability score (0-100)"""
        # Simple logic: lower payment relative to car price = better score
        if monthly_payment <= 0:
            return 100
        
        ratio = monthly_payment / (car_price / 60)  # Compare to 5-year loan at 0% interest
        score = max(0, min(100, 100 - (ratio * 100)))
        return round(score)
    
    def _calculate_average(self, numbers):
        """Calculate average of a list"""
        if not numbers:
            return 0
        return round(sum(numbers) / len(numbers), 2)



class ServiceCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ServiceCategory.objects.filter(is_active=True)
    serializer_class = ServiceCategorySerializer
    permission_classes = [AllowAny]
    
    @action(detail=True, methods=['get'])
    def services(self, request, pk=None):
        """Get all services for a category"""
        category = self.get_object()
        services = Service.objects.filter(
            category=category,
            is_active=True
        ).order_by('display_order')
        
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data)

class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filter by service type
        service_type = self.request.query_params.get('service_type')
        if service_type:
            queryset = queryset.filter(service_type=service_type)
        
        # Filter by car model (ElectricCar)
        car_model_id = self.request.query_params.get('car_model_id')
        if car_model_id:
            queryset = queryset.filter(
                Q(eligible_car_models__id=car_model_id) |
                Q(eligible_car_models__isnull=True)
            ).distinct()
        
        # Filter by manufacturer
        manufacturer_id = self.request.query_params.get('manufacturer_id')
        if manufacturer_id:
            queryset = queryset.filter(
                Q(eligible_manufacturers__id=manufacturer_id) |
                Q(eligible_manufacturers__isnull=True)
            ).distinct()
        
        # Filter featured services
        featured = self.request.query_params.get('featured')
        if featured:
            queryset = queryset.filter(is_featured=True)
        
        # Filter special offers
        special_offers = self.request.query_params.get('special_offers')
        if special_offers:
            queryset = queryset.filter(is_special_offer=True)
        
        # Filter NETA battery warranty
        neta_warranty = self.request.query_params.get('neta_warranty')
        if neta_warranty:
            queryset = queryset.filter(is_neta_battery_warranty=True)
        
        # Filter first round services
        first_round = self.request.query_params.get('first_round')
        if first_round:
            queryset = queryset.filter(is_first_round_service=True)
        
        return queryset.order_by('display_order')
    
    @action(detail=False, methods=['get'])
    def special_offers(self, request):
        """Get all current special offers"""
        today = date.today()
        offers = self.get_queryset().filter(
            is_special_offer=True,
            valid_from__lte=today,
            valid_until__gte=today
        )
        serializer = self.get_serializer(offers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def neta_services(self, request):
        """Get services specifically for NETA cars"""
        from cars.models import Manufacturer
        
        try:
            # Find NETA manufacturer
            neta_manufacturer = Manufacturer.objects.get(name__icontains='NETA')
            
            # Get services for NETA
            services = self.get_queryset().filter(
                Q(eligible_manufacturers=neta_manufacturer) |
                Q(is_neta_battery_warranty=True)
            ).distinct()
            
            serializer = self.get_serializer(services, many=True)
            return Response({
                'manufacturer': {
                    'id': neta_manufacturer.id,
                    'name': neta_manufacturer.name
                },
                'services': serializer.data,
                'count': services.count()
            })
            
        except Manufacturer.DoesNotExist:
            return Response(
                {'error': 'NETA manufacturer not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def for_electric_car(self, request):
        """Get services eligible for a specific electric car"""
        car_id = request.query_params.get('car_id')
        if not car_id:
            return Response(
                {'error': 'car_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from cars.models import ElectricCar
            car = ElectricCar.objects.get(id=car_id)
            
            # Get services eligible for this electric car
            services = self.get_queryset().filter(
                Q(eligible_car_models__id=car_id) |
                Q(eligible_manufacturers__id=car.manufacturer_id) |
                Q(eligible_car_models__isnull=True, eligible_manufacturers__isnull=True)
            ).distinct()
            
            # Categorize services
            categorized = {}
            for service in services:
                category_name = service.category.title if service.category else "General"
                if category_name not in categorized:
                    categorized[category_name] = []
                categorized[category_name].append(ServiceSerializer(service).data)
            
            return Response({
                'car': {
                    'id': car.id,
                    'name': car.display_name,
                    'manufacturer': car.manufacturer.name,
                    'model_year': car.model_year
                },
                'services': categorized,
                'total_count': services.count()
            })
            
        except ElectricCar.DoesNotExist:
            return Response(
                {'error': 'Electric car not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def first_round_services(self, request):
        """Get first round services for all cars"""
        services = self.get_queryset().filter(is_first_round_service=True)
        serializer = self.get_serializer(services, many=True)
        return Response(serializer.data)

class ServicePackageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ServicePackage.objects.filter(is_active=True)
    serializer_class = ServicePackageSerializer
    permission_classes = [AllowAny]

class ServiceFAQViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ServiceFAQ.objects.filter(is_active=True)
    serializer_class = ServiceFAQSerializer
    permission_classes = [AllowAny]

class ServiceTestimonialViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ServiceTestimonial.objects.filter(is_active=True)
    serializer_class = ServiceTestimonialSerializer
    permission_classes = [AllowAny]

class ServiceCenterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ServiceCenter.objects.filter(is_active=True)
    serializer_class = ServiceCenterSerializer
    permission_classes = [AllowAny]