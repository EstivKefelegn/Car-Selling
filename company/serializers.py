from rest_framework import serializers
from django.utils.text import slugify
from django.core.validators import EmailValidator
from .models import (
      AboutUs, TeamMember, DealershipPhoto, Event, EventCategory, EventTag, EventImage,
    EventSpeaker, EventSchedule, EventRegistration, News
)
from django.contrib.auth.models import User
import re
from django.utils import timezone

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



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = ['id', 'name', 'slug', 'description', 'icon', 'color']

class EventTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventTag
        fields = ['id', 'name', 'slug']

class EventImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventImage
        fields = ['id', 'image', 'caption', 'alt_text', 'display_order']

class EventSpeakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventSpeaker
        fields = [
            'id', 'name', 'title', 'company', 'bio',
            'photo', 'twitter', 'linkedin', 'website',
            'display_order'
        ]

class EventScheduleSerializer(serializers.ModelSerializer):
    speakers = EventSpeakerSerializer(many=True, read_only=True)
    
    class Meta:
        model = EventSchedule
        fields = [
            'id', 'day', 'start_time', 'end_time',
            'title', 'description', 'location', 'speakers'
        ]

class EventListSerializer(serializers.ModelSerializer):
    category = EventCategorySerializer(read_only=True)
    tags = EventTagSerializer(many=True, read_only=True)
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'description', 'event_type',
            'category', 'tags', 'start_date', 'end_date',
            'is_virtual', 'venue_name', 'city', 'country',
            'cover_image', 'is_featured', 'status',
            'requires_registration', 'is_free', 'price',
            'registration_open', 'seats_available',
            'duration_days'
        ]

class EventDetailSerializer(serializers.ModelSerializer):
    category = EventCategorySerializer(read_only=True)
    tags = EventTagSerializer(many=True, read_only=True)
    gallery = EventImageSerializer(many=True, read_only=True)
    speakers = EventSpeakerSerializer(many=True, read_only=True)
    schedules = EventScheduleSerializer(many=True, read_only=True)
    organizer = UserSerializer(read_only=True)
    registration_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'description', 'detailed_description',
            'event_type', 'category', 'tags', 'start_date', 'end_date',
            'timezone', 'is_virtual', 'venue_name', 'address', 'city',
            'state', 'country', 'zip_code', 'virtual_platform',
            'virtual_link', 'virtual_meeting_id', 'virtual_passcode',
            'cover_image', 'banner_image', 'gallery', 'speakers', 'schedules',
            'requires_registration', 'is_free', 'registration_link',
            'max_attendees', 'current_attendees', 'price', 'currency',
            'status', 'is_featured', 'is_private', 'organizer',
            'contact_person', 'contact_email', 'contact_phone',
            'created_at', 'updated_at', 'published_at', 'views',
            'registration_open', 'seats_available', 'duration_days',
            'registration_count'
        ]
    
    def get_registration_count(self, obj):
        return obj.registrations.filter(is_confirmed=True).count()

class EventRegistrationSerializer(serializers.ModelSerializer):
    event = EventListSerializer(read_only=True)
    event_id = serializers.PrimaryKeyRelatedField(
        queryset=Event.objects.filter(status__in=['upcoming', 'ongoing']),
        write_only=True,
        source='event'
    )
    
    class Meta:
        model = EventRegistration
        fields = [
            'id', 'event', 'event_id', 'full_name', 'email',
            'phone', 'company', 'job_title', 'dietary_preferences',
            'special_requirements', 'registration_date', 'is_confirmed',
            'checked_in', 'checkin_time', 'payment_status'
        ]
        read_only_fields = ['registration_date', 'is_confirmed', 'checked_in', 'checkin_time']
    
    def validate(self, data):
        event = data.get('event')
        email = data.get('email')
        
        # Check if event requires registration
        if not event.requires_registration:
            raise serializers.ValidationError(
                "This event does not require registration."
            )
        
        # Check if registration is open
        if not event.registration_open:
            raise serializers.ValidationError(
                "Registration is not open for this event."
            )
        
        # Check if email already registered
        if EventRegistration.objects.filter(event=event, email=email).exists():
            raise serializers.ValidationError(
                "This email is already registered for this event."
            )
        
        return data

class NewsSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = News
        fields = [
            'id', 'title', 'slug', 'description', 'content',
            'image', 'status', 'is_featured', 'author',
            'created_at', 'updated_at', 'published_at',
            'is_published', 'formatted_published_date', 'excerpt'
        ]
        read_only_fields = ['created_at', 'updated_at', 'slug']

class NewsListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = News
        fields = [
            'id', 'title', 'slug', 'description', 'excerpt',
            'image', 'is_featured', 'author', 'formatted_published_date'
        ]