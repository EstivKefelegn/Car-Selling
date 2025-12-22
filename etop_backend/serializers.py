from rest_framework import serializers
from django.utils.text import slugify
from django.core.validators import EmailValidator
from .models import (
    Manufacturer, CarColor, ElectricCar, CarColorImage, CarColorConfiguration, EVReview, EVComparison, EmailSubscriber, ContactOrder
)
from django.contrib.auth.models import User
import re



class ManufacturerSerializer(serializers.ModelSerializer):
    """Serializer for Manufacturer model"""
    logo_url = serializers.SerializerMethodField()
    car_count = serializers.IntegerField(read_only=True)
    ev_only_display = serializers.CharField(source='get_is_ev_only_display', read_only=True)
    
    class Meta:
        model = Manufacturer
        fields = [
            'id', 'name', 'country', 'founded_year', 'is_ev_only', 'ev_only_display',
            'description', 'logo', 'logo_url', 'website', 'headquarters', 'car_count', 'electric_cars', 'created_at', 'featured'
        ]
        read_only_fields = ['id', 'car_count', 'ev_only_display']
    
    def get_logo_url(self, obj):
        if obj.logo:
            return obj.logo.url
        return None
    
    def create(self, validated_data):
        # Ensure name is properly capitalized
        validated_data['name'] = validated_data['name'].title()
        return super().create(validated_data)


class ManufacturerListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Manufacturer lists"""
    logo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Manufacturer
        fields = ['id', 'name', 'country', 'logo_url', 'is_ev_only']
    
    def get_logo_url(self, obj):
        if obj.logo:
            return obj.logo.url
        return None


# ========== CAR COLOR SERIALIZERS ==========
class CarColorSerializer(serializers.ModelSerializer):
    """Serializer for CarColor model"""
    color_type_display = serializers.CharField(source='get_color_type_display', read_only=True)
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CarColor
        fields = [
            'id', 'name', 'hex_code', 'color_type', 'color_type_display',
            'image', 'image_url', 'description'
        ]
        read_only_fields = ['id', 'color_type_display']
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class CarColorListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for CarColor lists"""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CarColor
        fields = ['id', 'name', 'hex_code', 'color_type', 'image_url']
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


# ========== CAR COLOR IMAGE SERIALIZERS ==========
class CarColorImageSerializer(serializers.ModelSerializer):
    """Serializer for CarColorImage model"""
    car_name = serializers.CharField(source='car.display_name', read_only=True)
    exterior_color_name = serializers.CharField(source='exterior_color.name', read_only=True)
    interior_color_name = serializers.CharField(source='interior_color.name', read_only=True)
    image_type_display = serializers.CharField(source='get_image_type_display', read_only=True)
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CarColorImage
        fields = [
            'id', 'car', 'car_name', 'exterior_color', 'exterior_color_name',
            'interior_color', 'interior_color_name', 'image', 'image_url',
            'image_type', 'image_type_display', 'description', 'is_primary', 'order'
        ]
        read_only_fields = ['id', 'car_name', 'exterior_color_name', 'interior_color_name', 'image_type_display']
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None
    
    def validate(self, data):
        # Ensure at least one color is selected
        if not data.get('exterior_color') and not data.get('interior_color'):
            raise serializers.ValidationError("At least one color (exterior or interior) must be selected.")
        return data


class CarColorImageListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for CarColorImage lists"""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CarColorImage
        fields = ['id', 'image', 'image_url', 'image_type', 'is_primary', 'order']
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


# ========== CAR COLOR CONFIGURATION SERIALIZERS ==========
class CarColorConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for CarColorConfiguration model"""
    car_name = serializers.CharField(source='car.display_name', read_only=True)
    exterior_color_details = CarColorSerializer(source='exterior_color', read_only=True)
    interior_color_details = CarColorSerializer(source='interior_color', read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = CarColorConfiguration
        fields = [
            'id', 'car', 'car_name', 'exterior_color', 'exterior_color_details',
            'interior_color', 'interior_color_details', 'price_adjustment',
            'total_price', 'is_popular', 'is_available', 'delivery_time',
            'primary_image'
        ]
        read_only_fields = ['id', 'total_price', 'primary_image']
    
    def get_primary_image(self, obj):
        primary = obj.primary_image
        if primary and primary.image:
            return primary.image.url
        return None


# ========== ELECTRIC CAR SERIALIZERS ==========
class ElectricCarSerializer(serializers.ModelSerializer):
    """Full serializer for ElectricCar model"""
    # Related fields
    manufacturer_details = ManufacturerSerializer(source='manufacturer', read_only=True)
    available_exterior_colors = CarColorSerializer(many=True, read_only=True)
    available_interior_colors = CarColorSerializer(many=True, read_only=True)
    
    # Calculated fields
    efficiency = serializers.SerializerMethodField()
    charging_speed = serializers.SerializerMethodField()
    total_configurations = serializers.SerializerMethodField()
    is_available_for_sale = serializers.BooleanField(read_only=True)
    
    # Display fields
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    battery_type_display = serializers.CharField(source='get_battery_type_display', read_only=True)
    drive_type_display = serializers.CharField(source='get_drive_type_display', read_only=True)
    charging_type_display = serializers.CharField(source='get_charging_type_display', read_only=True)
    autopilot_level_display = serializers.CharField(source='get_autopilot_level_display', read_only=True)
    charging_port_location_display = serializers.CharField(source='get_charging_port_location_display', read_only=True)
    
    # Image URLs
    main_image_url = serializers.SerializerMethodField()
    brochure_url = serializers.SerializerMethodField()
    
    # Color images
    color_images = serializers.SerializerMethodField()
    color_configurations = serializers.SerializerMethodField()
    
    class Meta:
        model = ElectricCar
        fields = [
            'id', 'slug', 'manufacturer', 'manufacturer_details', 'model_name', 'variant',
            'model_year', 'category', 'category_display', 'status', 'status_display',
            'featured', 'battery_capacity', 'usable_battery', 'battery_type',
            'battery_type_display', 'battery_warranty_years', 'battery_warranty_km',
            'range_wltp', 'range_epa', 'energy_consumption', 'acceleration_0_100',
            'top_speed', 'motor_power', 'torque', 'drive_type', 'drive_type_display',
            'max_dc_charging', 'max_ac_charging', 'charging_type', 'charging_type_display',
            'charging_time_10_80', 'charging_time_0_100_ac', 'length', 'width', 'height',
            'wheelbase', 'curb_weight', 'cargo_capacity', 'seating_capacity',
            'available_exterior_colors', 'available_interior_colors',
            'has_heat_pump', 'has_battery_preconditioning', 'has_v2l', 'has_v2g',
            'has_one_pedal_driving', 'regen_braking_levels', 'autopilot_level',
            'autopilot_level_display', 'charging_port_location', 'charging_port_location_display',
            'base_price', 'estimated_delivery', 'tax_incentive', 'main_image',
            'main_image_url', 'brochure', 'brochure_url', 'description', 'key_features',
            'safety_features', 'efficiency', 'charging_speed', 'is_available_for_sale',
            'total_configurations', 'color_images', 'color_configurations',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = [
            'id', 'slug', 'efficiency', 'charging_speed', 'is_available_for_sale',
            'total_configurations', 'color_images', 'color_configurations', 'created_at',
            'updated_at', 'created_by'
        ]
        extra_kwargs = {
            'manufacturer': {'write_only': True},
            'available_exterior_colors': {'write_only': True},
            'available_interior_colors': {'write_only': True},
        }
    
    def get_main_image_url(self, obj):
        if obj.main_image:
            return obj.main_image.url
        return None
    
    def get_brochure_url(self, obj):
        if obj.brochure:
            return obj.brochure.url
        return None
    
    def get_efficiency(self, obj):
        return obj.efficiency
    
    def get_charging_speed(self, obj):
        return obj.charging_speed
    
    def get_total_configurations(self, obj):
        return obj.color_configurations.count()
    
    def get_color_images(self, obj):
        """Get all color images grouped by exterior/interior"""
        images = obj.color_images.all()
        return CarColorImageListSerializer(images, many=True).data
    
    def get_color_configurations(self, obj):
        """Get all available color configurations"""
        configs = obj.color_configurations.filter(is_available=True)
        return CarColorConfigurationSerializer(configs, many=True).data
    
    def create(self, validated_data):
        # Auto-generate slug if not provided
        if 'slug' not in validated_data or not validated_data['slug']:
            manufacturer_name = validated_data['manufacturer'].name
            model_name = validated_data['model_name']
            variant = validated_data.get('variant', '')
            year = validated_data['model_year']
            
            slug_parts = [manufacturer_name, model_name]
            if variant:
                slug_parts.append(variant)
            slug_parts.append(str(year))
            
            validated_data['slug'] = slugify('-'.join(slug_parts))
        
        # Set created_by user
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Update slug if name or model changes
        if 'model_name' in validated_data or 'variant' in validated_data:
            manufacturer_name = instance.manufacturer.name
            model_name = validated_data.get('model_name', instance.model_name)
            variant = validated_data.get('variant', instance.variant)
            year = instance.model_year
            
            slug_parts = [manufacturer_name, model_name]
            if variant:
                slug_parts.append(variant)
            slug_parts.append(str(year))
            
            validated_data['slug'] = slugify('-'.join(slug_parts))
        
        return super().update(instance, validated_data)


class ElectricCarListSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.CharField(source='manufacturer.name', read_only=True)
    manufacturer_logo = serializers.SerializerMethodField()
    main_image_url = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    efficiency = serializers.SerializerMethodField()
    total_configurations = serializers.SerializerMethodField()

    
    available_exterior_colors = serializers.SerializerMethodField()
    available_interior_colors = serializers.SerializerMethodField()

    class Meta:
        model = ElectricCar
        fields = [
            'id', 'slug', 'manufacturer_name', 'manufacturer_logo', 'model_name',
            'variant', 'model_year', 'category', 'category_display', 'status',
            'status_display', 'featured', 'range_wltp', 'acceleration_0_100',
            'motor_power', 'base_price', 'main_image_url', 'efficiency',
            'total_configurations', 'created_at',

            # 🚀 NEW COLOR FIELDS
            'available_exterior_colors',
            'available_interior_colors'
        ]

    def get_manufacturer_logo(self, obj):
        return obj.manufacturer.logo.url if obj.manufacturer.logo else None

    def get_main_image_url(self, obj):
        return obj.main_image.url if obj.main_image else None

    def get_efficiency(self, obj):
        return obj.efficiency

    def get_total_configurations(self, obj):
        return obj.color_configurations.count()

    def get_available_exterior_colors(self, obj):
        return [
            {
                "id": color.id,
                "name": color.name,
                "hex_code": color.hex_code,
                "type": "exterior",
            }
            for color in obj.available_exterior_colors.all()
        ]

    def get_available_interior_colors(self, obj):
        return [
            {
                "id": color.id,
                "name": color.name,
                "hex_code": color.hex_code,
                "type": "interior",
            }
            for color in obj.available_interior_colors.all()
        ]


class ElectricCarDetailSerializer(ElectricCarSerializer):
    """Extended serializer for detailed car view (no specification fields)."""

    # Only keep color gallery
    color_gallery = serializers.SerializerMethodField()

    class Meta(ElectricCarSerializer.Meta):
        fields = ElectricCarSerializer.Meta.fields + ['color_gallery']

    def get_color_gallery(self, obj):
        """Organize color images by type"""
        images = obj.color_images.all()
        
        # Group exterior images
        exterior_groups = {}
        for image in images.filter(exterior_color__isnull=False):
            color_name = image.exterior_color.name
            if color_name not in exterior_groups:
                exterior_groups[color_name] = {
                    'color': CarColorSerializer(image.exterior_color).data,
                    'images': []
                }
            exterior_groups[color_name]['images'].append(
                CarColorImageListSerializer(image).data
            )
        
        # Group interior images
        interior_groups = {}
        for image in images.filter(interior_color__isnull=False):
            color_name = image.interior_color.name
            if color_name not in interior_groups:
                interior_groups[color_name] = {
                    'color': CarColorSerializer(image.interior_color).data,
                    'images': []
                }
            interior_groups[color_name]['images'].append(
                CarColorImageListSerializer(image).data
            )

        return {
            'exterior_colors': list(exterior_groups.values()),
            'interior_colors': list(interior_groups.values())
        }



# ========== COMBINED SERIALIZERS ==========
class CarWithColorsSerializer(serializers.ModelSerializer):
    """Serializer for car with its color options"""
    manufacturer_details = ManufacturerListSerializer(source='manufacturer', read_only=True)
    available_exterior_colors = CarColorListSerializer(many=True, read_only=True)
    available_interior_colors = CarColorListSerializer(many=True, read_only=True)
    color_configurations = CarColorConfigurationSerializer(many=True, read_only=True)
    main_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ElectricCar
        fields = [
            'id', 'manufacturer_details', 'model_name', 'variant', 'model_year',
            'base_price', 'main_image_url', 'available_exterior_colors',
            'available_interior_colors', 'color_configurations'
        ]
    
    def get_main_image_url(self, obj):
        if obj.main_image:
            return obj.main_image.url
        return None


class ManufacturerWithCarsSerializer(ManufacturerSerializer):
    """Serializer for manufacturer with its cars"""
    cars = ElectricCarListSerializer(source='electric_cars', many=True, read_only=True)
    
    class Meta(ManufacturerSerializer.Meta):
        fields = ManufacturerSerializer.Meta.fields + ['cars']


# ========== CUSTOM FIELD SERIALIZERS ==========
class ColorChoiceSerializer(serializers.Serializer):
    """Serializer for color choices in forms"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    hex_code = serializers.CharField(allow_null=True)
    image_url = serializers.CharField(allow_null=True)


class CarConfigurationSerializer(serializers.Serializer):
    """Serializer for car configuration (used in frontend)"""
    car_id = serializers.IntegerField()
    exterior_color_id = serializers.IntegerField()
    interior_color_id = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    images = serializers.ListField(child=serializers.CharField())


class EVReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = EVReview
        fields = '__all__'
        read_only_fields = ['review_date']




class EVComparisonSerializer(serializers.ModelSerializer):
    cars = ElectricCarSerializer(many=True, read_only=True)
    car_ids = serializers.PrimaryKeyRelatedField(
        queryset=ElectricCar.objects.all(),
        source='cars',
        many=True,
        write_only=True
    )
    
    class Meta:
        model = EVComparison
        fields = '__all__'
        read_only_fields = ['created_at']


class EmailSubscriberSerializer(serializers.ModelSerializer):
    """Serializer for creating and retrieving email subscribers"""
    
    class Meta:
        model = EmailSubscriber
        fields = ['id', 'email', 'first_name', 'last_name', 
                 'sales_associate', 'subscription_status', 
                 'receive_inventory_alerts', 'subscribed_at']
        read_only_fields = ['id', 'subscription_status', 
                           'receive_inventory_alerts', 'subscribed_at']
    
    def validate_email(self, value):
        """Validate email format and uniqueness"""
        value = value.lower().strip()
        
        # Check if email already exists
        if EmailSubscriber.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "This email is already subscribed."
            )
        
        # Basic email format validation
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, value):
            raise serializers.ValidationError(
                "Please enter a valid email address."
            )
        
        return value
    
    def validate_sales_associate(self, value):
        """Ensure sales associate is a staff user if provided"""
        if value and not value.is_staff:
            raise serializers.ValidationError(
                "Selected user is not a valid sales associate."
            )
        return value
    
    def create(self, validated_data):
        """Create a new subscriber with default active status"""
        # Set default values
        validated_data['subscription_status'] = EmailSubscriber.SubscriptionStatus.ACTIVE
        validated_data['receive_inventory_alerts'] = True
        
        return super().create(validated_data)


class PublicEmailSubscriptionSerializer(serializers.Serializer):
    """Simplified serializer for public subscription (React frontend)"""
    
    email = serializers.EmailField(
        max_length=255,
        required=True,
        help_text="Subscriber's email address"
    )
    first_name = serializers.CharField(
        max_length=100, 
        required=False, 
        allow_blank=True,
        help_text="Optional first name"
    )
    last_name = serializers.CharField(
        max_length=100, 
        required=False, 
        allow_blank=True,
        help_text="Optional last name"
    )
    sales_associate_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Optional: ID of referring sales associate"
    )
    
    def validate_email(self, value):
        """Validate email format and uniqueness"""
        value = value.lower().strip()
        
        # Check if email already exists
        if EmailSubscriber.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "This email is already subscribed to our mailing list."
            )
        
        return value
    
    def create(self, validated_data):
        """Create a new email subscriber"""
        sales_associate_id = validated_data.pop('sales_associate_id', None)
        
        subscriber_data = {
            'email': validated_data['email'],
            'first_name': validated_data.get('first_name', ''),
            'last_name': validated_data.get('last_name', ''),
            'subscription_status': EmailSubscriber.SubscriptionStatus.ACTIVE,
            'receive_inventory_alerts': True,
        }
        
        # Add sales associate if provided
        if sales_associate_id:
            from django.contrib.auth.models import User
            try:
                sales_associate = User.objects.get(
                    id=sales_associate_id, 
                    is_staff=True
                )
                subscriber_data['sales_associate'] = sales_associate
            except User.DoesNotExist:
                # Silently ignore invalid sales associate IDs
                pass
        
        return EmailSubscriber.objects.create(**subscriber_data)


class SubscriptionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating subscription preferences"""
    
    class Meta:
        model = EmailSubscriber
        fields = ['receive_inventory_alerts']
    
    def update(self, instance, validated_data):
        instance.receive_inventory_alerts = validated_data.get(
            'receive_inventory_alerts', 
            instance.receive_inventory_alerts
        )
        instance.save()
        return instance


class UnsubscribeSerializer(serializers.Serializer):
    """Serializer for unsubscribing"""
    
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        value = value.lower().strip()
        
        # Check if email exists
        if not EmailSubscriber.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "No subscription found with this email address."
            )
        
        return value
    
    def unsubscribe(self):
        """Perform the unsubscribe action"""
        email = self.validated_data['email']
        try:
            subscriber = EmailSubscriber.objects.get(email=email)
            subscriber.unsubscribe()
            return {
                'success': True,
                'message': 'You have been unsubscribed successfully.'
            }
        except EmailSubscriber.DoesNotExist:
            return {
                'success': False,
                'message': 'No subscription found.'
            }
class SalesAssociateSerializer(serializers.ModelSerializer):
    """Serializer for sales associates (staff users)"""
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username        

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import CustomerVehicle, ServiceBooking, ServiceReminder
from datetime import datetime
import json

# Use your existing UserSerializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class CustomerVehicleSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    make = serializers.SerializerMethodField(read_only=True)
    model = serializers.SerializerMethodField(read_only=True)
    year = serializers.SerializerMethodField(read_only=True)
    display_name = serializers.SerializerMethodField(read_only=True)
    is_warranty_valid = serializers.BooleanField(read_only=True)
    needs_10000km_service = serializers.BooleanField(read_only=True)
    kilometers_since_last_service = serializers.IntegerField(read_only=True)
    days_until_warranty_expires = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = CustomerVehicle
        fields = '__all__'
        read_only_fields = ('customer', 'created_at', 'updated_at')
    
    def get_make(self, obj):
        return obj.make
    
    def get_model(self, obj):
        return obj.model
    
    def get_year(self, obj):
        return obj.year
    
    def get_display_name(self, obj):
        return obj.display_name
    
    def validate(self, data):
        # Validate VIN length
        vin = data.get('vin', '')
        if vin and len(vin) != 17:
            raise serializers.ValidationError({
                'vin': 'VIN must be 17 characters long'
            })
        
        # Validate current odometer
        current_odometer = data.get('current_odometer')
        if current_odometer and current_odometer < 0:
            raise serializers.ValidationError({
                'current_odometer': 'Odometer reading cannot be negative'
            })
        
        return data

class ServiceBookingSerializer(serializers.ModelSerializer):
    # Plain strings for customer info
    customer_name = serializers.CharField(read_only=True)
    customer_email = serializers.CharField(read_only=True)

    vehicle_display = serializers.SerializerMethodField(read_only=True)
    service_type_display = serializers.SerializerMethodField(read_only=True)
    status_display = serializers.SerializerMethodField(read_only=True)
    priority_display = serializers.SerializerMethodField(read_only=True)
    is_neta_warranty_booking = serializers.BooleanField(read_only=True)
    is_10000km_service_booking = serializers.BooleanField(read_only=True)
    scheduled_datetime = serializers.DateTimeField(read_only=True)
    days_until_scheduled = serializers.IntegerField(read_only=True)

    class Meta:
        model = ServiceBooking
        fields = '__all__'
        read_only_fields = (
            'booking_number', 'customer', 'customer_email',
            'status', 'created_at', 'updated_at', 'scheduled_at', 'completed_at'
        )

    def get_vehicle_display(self, obj):
        return obj.vehicle.display_name

    def get_service_type_display(self, obj):
        return obj.get_service_type_display()

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_priority_display(self, obj):
        return obj.get_priority_display()

    def validate(self, data):
        # Validate preferred date is not in the past
        preferred_date = data.get('preferred_date')
        if preferred_date and preferred_date < datetime.now().date():
            raise serializers.ValidationError({
                'preferred_date': 'Preferred date cannot be in the past'
            })

        # Validate alternative dates format
        alternative_dates = data.get('alternative_dates', [])
        if alternative_dates:
            if isinstance(alternative_dates, str):
                try:
                    alternative_dates = json.loads(alternative_dates)
                except json.JSONDecodeError:
                    raise serializers.ValidationError({
                        'alternative_dates': 'Invalid date format. Use JSON list of YYYY-MM-DD strings'
                    })
            for date_str in alternative_dates:
                try:
                    datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    raise serializers.ValidationError({
                        'alternative_dates': 'Invalid date format. Use YYYY-MM-DD'
                    })
        return data

class ServiceBookingCreateSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(write_only=True, required=True)
    phone = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = ServiceBooking
        fields = (
            'vehicle', 'service_type', 'service_type_custom',
            'preferred_date', 'preferred_time_slot', 'alternative_dates',
            'odometer_reading', 'service_description', 'symptoms_problems',
            'customer_notes', 'full_name', 'email', 'phone'
        )

    def validate(self, data):
        vehicle = data.get('vehicle')
        if not vehicle:
            raise serializers.ValidationError({'vehicle': 'Vehicle is required.'})
        return data

    def create(self, validated_data):
        # Extract customer info
        full_name = validated_data.pop('full_name')
        email = validated_data.pop('email')
        validated_data.pop('phone', None)

        # Assign as strings
        validated_data['customer'] = full_name
        validated_data['customer_email'] = email

        booking = ServiceBooking.objects.create(**validated_data)
        return booking


class ServiceReminderSerializer(serializers.ModelSerializer):
    reminder_type_display = serializers.SerializerMethodField()
    vehicle_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceReminder
        fields = '__all__'
    
    def get_reminder_type_display(self, obj):
        return obj.get_reminder_type_display()
    
    def get_vehicle_display(self, obj):
        return obj.vehicle.display_name

class PublicServiceBookingSerializer(serializers.ModelSerializer):
    # Write-only fields for customer input
    full_name = serializers.CharField(write_only=True, required=True, max_length=255)
    email = serializers.EmailField(write_only=True, required=True, max_length=255)
    phone = serializers.CharField(write_only=True, required=True, max_length=20)

    class Meta:
        model = ServiceBooking
        fields = (
            'vehicle', 'service_type', 'service_type_custom',
            'preferred_date', 'preferred_time_slot', 'alternative_dates',
            'odometer_reading', 'service_description', 'symptoms_problems',
            'customer_notes', 'full_name', 'email', 'phone'
        )

    def validate(self, data):
        # Validate vehicle exists
        vehicle = data.get('vehicle')
        if not vehicle:
            raise serializers.ValidationError({'vehicle': 'Vehicle is required.'})
        
        # Validate required service type
        service_type = data.get('service_type')
        if not service_type:
            raise serializers.ValidationError({'service_type': 'Service type is required.'})
        
        # Validate odometer reading for certain service types
        if service_type == '10000km_service' and not data.get('odometer_reading'):
            raise serializers.ValidationError({
                'odometer_reading': 'Odometer reading is required for 10,000 KM service.'
            })
        
        # Validate preferred date is not in the past
        preferred_date = data.get('preferred_date')
        if preferred_date and preferred_date < datetime.now().date():
            raise serializers.ValidationError({
                'preferred_date': 'Preferred date cannot be in the past.'
            })

        # Validate alternative dates format
        alternative_dates = data.get('alternative_dates', [])
        if alternative_dates:
            if isinstance(alternative_dates, str):
                try:
                    alternative_dates = json.loads(alternative_dates)
                except json.JSONDecodeError:
                    raise serializers.ValidationError({
                        'alternative_dates': 'Invalid date format. Use JSON list of YYYY-MM-DD strings'
                    })
            
            for date_str in alternative_dates:
                try:
                    datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    raise serializers.ValidationError({
                        'alternative_dates': f'Invalid date format: {date_str}. Use YYYY-MM-DD'
                    })
        
        return data

    def create(self, validated_data):
        # Extract customer info
        full_name = validated_data.pop('full_name')
        email = validated_data.pop('email')
        phone = validated_data.pop('phone')
        
        # Assign customer information to model fields
        validated_data['customer'] = full_name
        validated_data['customer_email'] = email
        
        # Phone field - you need to decide where to store it
        # Option 1: Add customer_phone field to model (recommended)
        # Option 2: Store in customer_notes for now
        
        # For now, append phone to customer_notes
        existing_notes = validated_data.get('customer_notes', '')
        if existing_notes:
            validated_data['customer_notes'] = f"{existing_notes}\nPhone: {phone}"
        else:
            validated_data['customer_notes'] = f"Phone: {phone}"
        
        # Set default values for required fields that might be missing
        if 'odometer_reading' not in validated_data:
            validated_data['odometer_reading'] = 0
        
        if 'preferred_time_slot' not in validated_data or not validated_data['preferred_time_slot']:
            # Set a default time slot if not provided
            validated_data['preferred_time_slot'] = timezone.now().time()
        
        # Ensure alternative_dates is a list
        alternative_dates = validated_data.get('alternative_dates', [])
        if isinstance(alternative_dates, str):
            try:
                validated_data['alternative_dates'] = json.loads(alternative_dates)
            except:
                validated_data['alternative_dates'] = []
        
        # Create the booking
        booking = ServiceBooking.objects.create(**validated_data)
        
        # Try to send booking confirmation email
        try:
            self._send_booking_confirmation_email(booking, full_name, email, phone)
        except Exception as e:
            # Log but don't fail the booking creation
            print(f"Failed to send booking confirmation email: {e}")
        
        return booking
    
    def _send_booking_confirmation_email(self, booking, full_name, email, phone):
        """Send booking confirmation email"""
        from django.core.mail import EmailMessage
        from django.template.loader import render_to_string
        
        context = {
            'booking': booking,
            'customer_name': full_name,
            'customer_email': email,
            'customer_phone': phone,
            'booking_number': booking.booking_number,
            'vehicle': booking.vehicle.display_name if booking.vehicle else 'Unknown Vehicle',
            'service_type': booking.get_service_type_display(),
            'preferred_date': booking.preferred_date.strftime('%B %d, %Y') if booking.preferred_date else 'Not specified',
        }
        
        html_content = render_to_string('emails/booking_received.html', context)
        
        email_message = EmailMessage(
            subject=f'Service Booking Received - #{booking.booking_number}',
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
            reply_to=[settings.SERVICE_EMAIL] if hasattr(settings, 'SERVICE_EMAIL') else None
        )
        email_message.content_subtype = 'html'
        email_message.send(fail_silently=True)
        
class VehicleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating vehicles with validation"""
    
    class Meta:
        model = CustomerVehicle
        exclude = ('customer', 'created_at', 'updated_at')
    
    def validate(self, data):
        # Ensure either electric_car or custom details are provided
        electric_car = data.get('electric_car')
        custom_make = data.get('custom_make')
        custom_model = data.get('custom_model')
        
        if not electric_car and (not custom_make or not custom_model):
            raise serializers.ValidationError({
                'custom_make': 'Either select an electric car or provide custom make and model',
                'custom_model': 'Either select an electric car or provide custom make and model'
            })
        
        # Validate VIN length
        vin = data.get('vin', '')
        if len(vin) != 17:
            raise serializers.ValidationError({
                'vin': 'VIN must be exactly 17 characters'
            })
        
        # Validate license plate format
        license_plate = data.get('license_plate', '')
        if not license_plate:
            raise serializers.ValidationError({
                'license_plate': 'License plate is required'
            })
        
        return data
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['customer'] = request.user
        
        return super().create(validated_data)


class ContactOrderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer used when user submits the contact/order form
    """

    electric_car_id = serializers.PrimaryKeyRelatedField(
        queryset=ElectricCar.objects.all(),
        source='electric_car',
        write_only=True
    )

    class Meta:
        model = ContactOrder
        fields = [
            'full_name',
            'phone_number',
            'electric_car_id',
            'preferred_contact_time',
        ]

    def create(self, validated_data):
        """
        Message is auto-generated in model save()
        """
        return ContactOrder.objects.create(**validated_data)

class ContactOrderSerializer(serializers.ModelSerializer):
    electric_car = serializers.SerializerMethodField()
    preferred_contact_time_display = serializers.CharField(
        source='get_preferred_contact_time_display',
        read_only=True
    )

    class Meta:
        model = ContactOrder
        fields = [
            'id',
            'full_name',
            'phone_number',
            'electric_car',
            'message',
            'preferred_contact_time',
            'preferred_contact_time_display',
            'status',
            'created_at',
        ]

    def get_electric_car(self, obj):
        return {
            'id': obj.electric_car.id,
            'name': obj.electric_car.display_name,
            'slug': obj.electric_car.slug,
            'model_year': obj.electric_car.model_year,
        }
