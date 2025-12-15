from rest_framework import serializers
from django.utils.text import slugify
from django.core.validators import EmailValidator
from .models import (
    Manufacturer, CarColor, ElectricCar, CarColorImage, CarColorConfiguration, EVReview, EVComparison, EmailSubscriber, AboutUs, TeamMember, DealershipPhoto
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
            'description', 'logo', 'logo_url', 'website', 'headquarters', 'car_count', 'electric_cars'
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



class DealershipPhotoSerializer(serializers.ModelSerializer):
    """Serializer for dealership photos"""
    
    photo_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = DealershipPhoto
        fields = [
            'id', 'photo', 'photo_url', 'thumbnail_url', 'caption', 
            'photo_type', 'display_order', 'is_active', 'uploaded_at'
        ]
        read_only_fields = ['uploaded_at']
    
    def get_photo_url(self, obj):
        """Get absolute URL for the photo"""
        if obj.photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return None
    
    def get_thumbnail_url(self, obj):
        """Get thumbnail URL (you can implement thumbnail generation)"""
        # If you want to create thumbnails, you can use:
        # from django.core.files.storage import default_storage
        # from django.core.files.base import ContentFile
        # Or use sorl-thumbnail library
        return self.get_photo_url(obj)


class TeamMemberSerializer(serializers.ModelSerializer):
    """Serializer for team members"""
    
    photo_url = serializers.SerializerMethodField()
    display_position = serializers.CharField(read_only=True)
    
    class Meta:
        model = TeamMember
        fields = [
            'id', 'full_name', 'position', 'custom_position', 'display_position',
            'bio', 'photo', 'photo_url', 'email', 'phone', 'years_experience',
            'is_active', 'display_order', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_photo_url(self, obj):
        """Get absolute URL for team member photo"""
        if obj.photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return None
    
    def validate_phone(self, value):
        """Validate phone number format"""
        if value:
            phone_pattern = r'^[\d\s\-\+\(\)]{10,20}$'
            if not re.match(phone_pattern, value):
                raise serializers.ValidationError("Please enter a valid phone number.")
        return value
    
    def validate_email(self, value):
        """Validate email format"""
        if value:
            validator = EmailValidator()
            try:
                validator(value)
            except:
                raise serializers.ValidationError("Please enter a valid email address.")
        return value
    
    def validate(self, data):
        """Custom validation"""
        # If position is 'other', custom_position must be provided
        if data.get('position') == 'other' and not data.get('custom_position'):
            raise serializers.ValidationError({
                'custom_position': 'Custom position is required when position is "Other".'
            })
        return data


class BusinessHoursSerializer(serializers.Serializer):
    """Serializer for business hours"""
    
    day = serializers.CharField(source='get_day_display')
    open_time = serializers.TimeField(format='%I:%M %p')
    close_time = serializers.TimeField(format='%I:%M %p')
    is_open = serializers.BooleanField()


class AboutUsSerializer(serializers.ModelSerializer):
    """Main serializer for About Us information"""
    
    # Nested serializers
    team_members = TeamMemberSerializer(many=True, read_only=True)
    photos = DealershipPhotoSerializer(many=True, read_only=True)
    
    # Computed fields
    full_address = serializers.CharField(read_only=True)
    coordinates = serializers.SerializerMethodField()
    google_maps_url = serializers.CharField(read_only=True)
    business_hours = serializers.SerializerMethodField()
    social_media_links = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = AboutUs
        fields = [
            # Basic Information
            'id', 'dealership_name', 'tagline', 'logo', 'logo_url', 'description',
            
            # Location
            'address', 'city', 'state_province', 'postal_code', 'country',
            'full_address', 'latitude', 'longitude', 'coordinates',
            'map_zoom_level', 'google_maps_url',
            
            # Contact
            'phone_number', 'secondary_phone', 'email', 'support_email', 'website',
            
            # Business Hours
            'monday_open', 'monday_close',
            'tuesday_open', 'tuesday_close',
            'wednesday_open', 'wednesday_close',
            'thursday_open', 'thursday_close',
            'friday_open', 'friday_close',
            'saturday_open', 'saturday_close',
            'sunday_open', 'sunday_close',
            'business_hours',
            
            # Social Media
            'facebook_url', 'twitter_url', 'instagram_url',
            'linkedin_url', 'youtube_url', 'social_media_links',
            
            # About Content
            'mission_statement', 'vision_statement', 'core_values', 'history',
            
            # Services
            'services_offered', 'brands_carried',
            
            # Related Data
            'team_members', 'photos',
            
            # Metadata
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_coordinates(self, obj):
        """Get coordinates as a dictionary"""
        return {
            'latitude': float(obj.latitude),
            'longitude': float(obj.longitude)
        }
    
    def get_logo_url(self, obj):
        """Get absolute URL for logo"""
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None
    
    def get_business_hours(self, obj):
        """Get formatted business hours"""
        hours_data = []
        
        days_config = [
            ('Monday', obj.monday_open, obj.monday_close),
            ('Tuesday', obj.tuesday_open, obj.tuesday_close),
            ('Wednesday', obj.wednesday_open, obj.wednesday_close),
            ('Thursday', obj.thursday_open, obj.thursday_close),
            ('Friday', obj.friday_open, obj.friday_close),
            ('Saturday', obj.saturday_open, obj.saturday_close),
        ]
        
        # Add Sunday if set
        if obj.sunday_open and obj.sunday_close:
            days_config.append(('Sunday', obj.sunday_open, obj.sunday_close))
        
        for day_name, open_time, close_time in days_config:
            if open_time and close_time:
                hours_data.append({
                    'day': day_name,
                    'open_time': open_time.strftime('%I:%M %p'),
                    'close_time': close_time.strftime('%I:%M %p'),
                    'is_open': True
                })
            else:
                hours_data.append({
                    'day': day_name,
                    'open_time': None,
                    'close_time': None,
                    'is_open': False
                })
        
        return hours_data
    
    def get_social_media_links(self, obj):
        """Get social media links as dictionary"""
        links = {}
        if obj.facebook_url:
            links['facebook'] = obj.facebook_url
        if obj.twitter_url:
            links['twitter'] = obj.twitter_url
        if obj.instagram_url:
            links['instagram'] = obj.instagram_url
        if obj.linkedin_url:
            links['linkedin'] = obj.linkedin_url
        if obj.youtube_url:
            links['youtube'] = obj.youtube_url
        return links
    
    def validate_latitude(self, value):
        """Validate latitude range"""
        if not -90 <= float(value) <= 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90.")
        return value
    
    def validate_longitude(self, value):
        """Validate longitude range"""
        if not -180 <= float(value) <= 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180.")
        return value
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        phone_pattern = r'^[\d\s\-\+\(\)]{10,20}$'
        if not re.match(phone_pattern, value):
            raise serializers.ValidationError("Please enter a valid phone number.")
        return value
    
    def validate_map_zoom_level(self, value):
        """Validate map zoom level"""
        if not 1 <= value <= 20:
            raise serializers.ValidationError("Zoom level must be between 1 and 20.")
        return value


# Simplified serializers for public API
class PublicAboutUsSerializer(serializers.ModelSerializer):
    """Simplified serializer for public API (read-only)"""
    
    logo_url = serializers.SerializerMethodField()
    full_address = serializers.CharField(read_only=True)
    coordinates = serializers.SerializerMethodField()
    business_hours_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = AboutUs
        fields = [
            'dealership_name', 'tagline', 'logo_url', 'description',
            'full_address', 'coordinates',
            'phone_number', 'email', 'website',
            'facebook_url', 'instagram_url', 'twitter_url',
            'business_hours_summary'
        ]
        read_only = True
    
    def get_logo_url(self, obj):
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None
    
    def get_coordinates(self, obj):
        return {
            'latitude': float(obj.latitude),
            'longitude': float(obj.longitude)
        }
    
    def get_business_hours_summary(self, obj):
        """Get simplified business hours"""
        if obj.monday_open and obj.friday_close:
            return f"Mon-Fri: {obj.monday_open.strftime('%I:%M %p')} - {obj.friday_close.strftime('%I:%M %p')}"
        return "Contact for hours"


class AboutUsCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating AboutUs (admin only)"""
    
    class Meta:
        model = AboutUs
        fields = [
            'dealership_name', 'tagline', 'logo', 'description',
            'address', 'city', 'state_province', 'postal_code', 'country',
            'latitude', 'longitude', 'map_zoom_level',
            'phone_number', 'secondary_phone', 'email', 'support_email', 'website',
            'facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url', 'youtube_url',
            'mission_statement', 'vision_statement', 'core_values', 'history',
            'services_offered', 'brands_carried',
            'is_active'
        ]
    
    def validate(self, data):
        """Custom validation for business logic"""
        # Ensure only one active AboutUs entry exists
        if data.get('is_active', True):
            # Exclude current instance if updating
            instance = getattr(self, 'instance', None)
            if instance:
                active_count = AboutUs.objects.filter(is_active=True).exclude(id=instance.id).count()
            else:
                active_count = AboutUs.objects.filter(is_active=True).count()
            
            if active_count > 0:
                raise serializers.ValidationError({
                    'is_active': 'Only one About Us entry can be active at a time.'
                })
        
        return data


# Serializer for bulk operations
class AboutUsBulkSerializer(serializers.Serializer):
    """Serializer for bulk operations"""
    
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of AboutUs IDs"
    )
    
    action = serializers.ChoiceField(
        choices=['activate', 'deactivate', 'delete'],
        help_text="Action to perform"
    )        