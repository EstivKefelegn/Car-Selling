from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from ckeditor.fields import RichTextField  
from django.core.validators import MinValueValidator, MaxValueValidator

import re


class AboutUs(models.Model):
    """
    Model to store dealership information including location coordinates
    """
    
    class Meta:
        verbose_name = _("About Us")
        verbose_name_plural = _("About Us")
    
    # ====================
    # BASIC INFORMATION
    # ====================
    dealership_name = models.CharField(
        max_length=200,
        verbose_name=_("Dealership Name"),
        help_text=_("The official name of your dealership")
    )
    
    tagline = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Tagline/Slogan"),
        help_text=_("Your dealership's tagline or slogan")
    )
    
    logo = models.ImageField(
        upload_to='dealership/logos/',
        blank=True,
        null=True,
        verbose_name=_("Dealership Logo"),
        help_text=_("Upload your dealership logo")
    )
    
    # ====================
    # LOCATION & COORDINATES
    # ====================
    address = models.TextField(
        verbose_name=_("Full Address"),
        help_text=_("Complete physical address")
    )
    
    city = models.CharField(
        max_length=100,
        verbose_name=_("City")
    )
    
    state_province = models.CharField(
        max_length=100,
        verbose_name=_("State/Province")
    )
    
    postal_code = models.CharField(
        max_length=20,
        verbose_name=_("Postal/ZIP Code")
    )
    
    country = models.CharField(
        max_length=100,
        default="Ethiopia",
        verbose_name=_("Country")
    )
    
    # Geographic coordinates
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name=_("Latitude"),
        help_text=_("GPS latitude coordinate (e.g., 9.019150)")
    )
    
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name=_("Longitude"),
        help_text=_("GPS longitude coordinate (e.g., 38.752869)")
    )
    
    # Map settings
    map_zoom_level = models.IntegerField(
        default=15,
        verbose_name=_("Map Zoom Level"),
        help_text=_("Default zoom level for maps (1-20)")
    )
    
    # ====================
    # CONTACT INFORMATION
    # ====================
    phone_number = models.CharField(
        max_length=20,
        verbose_name=_("Primary Phone"),
        help_text=_("Main contact phone number")
    )
    
    secondary_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Secondary Phone"),
        help_text=_("Additional phone number")
    )
    
    email = models.EmailField(
        verbose_name=_("Email Address"),
        help_text=_("Primary contact email")
    )
    
    support_email = models.EmailField(
        blank=True,
        verbose_name=_("Support Email"),
        help_text=_("Customer support email")
    )
    
    website = models.URLField(
        max_length=200,
        blank=True,
        verbose_name=_("Website URL"),
        help_text=_("Official website address")
    )
    
    # ====================
    # BUSINESS HOURS
    # ====================
    monday_open = models.TimeField(
        default='08:00',
        verbose_name=_("Monday Open")
    )
    monday_close = models.TimeField(
        default='18:00',
        verbose_name=_("Monday Close")
    )
    
    tuesday_open = models.TimeField(
        default='08:00',
        verbose_name=_("Tuesday Open")
    )
    tuesday_close = models.TimeField(
        default='18:00',
        verbose_name=_("Tuesday Close")
    )
    
    wednesday_open = models.TimeField(
        default='08:00',
        verbose_name=_("Wednesday Open")
    )
    wednesday_close = models.TimeField(
        default='18:00',
        verbose_name=_("Wednesday Close")
    )
    
    thursday_open = models.TimeField(
        default='08:00',
        verbose_name=_("Thursday Open")
    )
    thursday_close = models.TimeField(
        default='18:00',
        verbose_name=_("Thursday Close")
    )
    
    friday_open = models.TimeField(
        default='08:00',
        verbose_name=_("Friday Open")
    )
    friday_close = models.TimeField(
        default='18:00',
        verbose_name=_("Friday Close")
    )
    
    saturday_open = models.TimeField(
        default='09:00',
        verbose_name=_("Saturday Open")
    )
    saturday_close = models.TimeField(
        default='17:00',
        verbose_name=_("Saturday Close")
    )
    
    sunday_open = models.TimeField(
        default='10:00',
        blank=True,
        null=True,
        verbose_name=_("Sunday Open")
    )
    sunday_close = models.TimeField(
        default='16:00',
        blank=True,
        null=True,
        verbose_name=_("Sunday Close")
    )
    
    # ====================
    # SOCIAL MEDIA
    # ====================
    facebook_url = models.URLField(
        max_length=200,
        blank=True,
        verbose_name=_("Facebook URL")
    )
    
    twitter_url = models.URLField(
        max_length=200,
        blank=True,
        verbose_name=_("Twitter/X URL")
    )
    
    instagram_url = models.URLField(
        max_length=200,
        blank=True,
        verbose_name=_("Instagram URL")
    )
    
    linkedin_url = models.URLField(
        max_length=200,
        blank=True,
        verbose_name=_("LinkedIn URL")
    )
    
    youtube_url = models.URLField(
        max_length=200,
        blank=True,
        verbose_name=_("YouTube URL")
    )
    
    # ====================
    # ABOUT CONTENT
    # ====================
    description = models.TextField(
        verbose_name=_("Description"),
        help_text=_("Detailed description of your dealership")
    )
    
    mission_statement = models.TextField(
        blank=True,
        verbose_name=_("Mission Statement"),
        help_text=_("Your dealership's mission statement")
    )
    
    vision_statement = models.TextField(
        blank=True,
        verbose_name=_("Vision Statement"),
        help_text=_("Your dealership's vision statement")
    )
    
    core_values = models.TextField(
        blank=True,
        verbose_name=_("Core Values"),
        help_text=_("List your core values")
    )
    
    history = models.TextField(
        blank=True,
        verbose_name=_("History"),
        help_text=_("Brief history of your dealership")
    )
    
    # ====================
    # SERVICES
    # ====================
    services_offered = models.TextField(
        blank=True,
        verbose_name=_("Services Offered"),
        help_text=_("List services offered (e.g., Financing, Trade-ins, Maintenance)")
    )
    
    brands_carried = models.TextField(
        blank=True,
        verbose_name=_("Brands Carried"),
        help_text=_("List of car brands you carry")
    )
    
    # ====================
    # METADATA
    # ====================
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Set to active to display on website")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At")
    )
    
    # ====================
    # METHODS
    # ====================
    def __str__(self):
        return self.dealership_name
    
    def clean(self):
        """Validate model data"""
        super().clean()
        
        # Validate phone numbers
        phone_pattern = r'^[\d\s\-\+\(\)]{10,20}$'
        if not re.match(phone_pattern, self.phone_number):
            raise ValidationError({'phone_number': _('Please enter a valid phone number.')})
        
        if self.secondary_phone and not re.match(phone_pattern, self.secondary_phone):
            raise ValidationError({'secondary_phone': _('Please enter a valid phone number.')})
        
        # Validate coordinates
        if not -90 <= float(self.latitude) <= 90:
            raise ValidationError({'latitude': _('Latitude must be between -90 and 90.')})
        
        if not -180 <= float(self.longitude) <= 180:
            raise ValidationError({'longitude': _('Longitude must be between -180 and 180.')})
        
        # Validate map zoom
        if not 1 <= self.map_zoom_level <= 20:
            raise ValidationError({'map_zoom_level': _('Zoom level must be between 1 and 20.')})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def full_address(self):
        """Get complete formatted address"""
        parts = [
            self.address,
            self.city,
            self.state_province,
            self.postal_code,
            self.country
        ]
        return ', '.join(filter(None, parts))
    
    @property
    def coordinates(self):
        """Get coordinates as tuple"""
        return (float(self.latitude), float(self.longitude))
    
    @property
    def google_maps_url(self):
        """Generate Google Maps URL"""
        return f"https://www.google.com/maps?q={self.latitude},{self.longitude}"
    
    @property
    def business_hours(self):
        """Get formatted business hours"""
        hours = []
        
        days = [
            ('Monday', self.monday_open, self.monday_close),
            ('Tuesday', self.tuesday_open, self.tuesday_close),
            ('Wednesday', self.wednesday_open, self.wednesday_close),
            ('Thursday', self.thursday_open, self.thursday_close),
            ('Friday', self.friday_open, self.friday_close),
            ('Saturday', self.saturday_open, self.saturday_close),
        ]
        
        if self.sunday_open and self.sunday_close:
            days.append(('Sunday', self.sunday_open, self.sunday_close))
        
        for day, open_time, close_time in days:
            if open_time and close_time:
                hours.append(f"{day}: {open_time.strftime('%I:%M %p')} - {close_time.strftime('%I:%M %p')}")
        
        return hours
    
    @property
    def social_media_links(self):
        """Get all social media links"""
        links = {}
        if self.facebook_url:
            links['Facebook'] = self.facebook_url
        if self.twitter_url:
            links['Twitter'] = self.twitter_url
        if self.instagram_url:
            links['Instagram'] = self.instagram_url
        if self.linkedin_url:
            links['LinkedIn'] = self.linkedin_url
        if self.youtube_url:
            links['YouTube'] = self.youtube_url
        return links
    
    @classmethod
    def get_active(cls):
        """Get active AboutUs entry"""
        return cls.objects.filter(is_active=True).first()


class TeamMember(models.Model):
    """
    Model to store team members/staff information
    """
    
    class PositionChoices(models.TextChoices):
        OWNER = 'owner', _('Owner')
        MANAGER = 'manager', _('Manager')
        SALES = 'sales', _('Sales Associate')
        MECHANIC = 'mechanic', _('Mechanic')
        FINANCE = 'finance', _('Finance Manager')
        CUSTOMER_SERVICE = 'customer_service', _('Customer Service')
        OTHER = 'other', _('Other')
    
    about_us = models.ForeignKey(
        AboutUs,
        on_delete=models.CASCADE,
        related_name='team_members',
        verbose_name=_("Dealership")
    )
    
    full_name = models.CharField(
        max_length=100,
        verbose_name=_("Full Name")
    )
    
    position = models.CharField(
        max_length=50,
        choices=PositionChoices.choices,
        verbose_name=_("Position")
    )
    
    custom_position = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Custom Position"),
        help_text=_("If 'Other' is selected, specify position here")
    )
    
    bio = models.TextField(
        blank=True,
        verbose_name=_("Biography")
    )
    
    photo = models.ImageField(
        upload_to='team/photos/',
        blank=True,
        null=True,
        verbose_name=_("Photo")
    )
    
    email = models.EmailField(
        blank=True,
        verbose_name=_("Email")
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Phone")
    )
    
    years_experience = models.IntegerField(
        default=0,
        verbose_name=_("Years of Experience")
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active")
    )
    
    display_order = models.IntegerField(
        default=0,
        verbose_name=_("Display Order"),
        help_text=_("Order in which team members are displayed")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Team Member")
        verbose_name_plural = _("Team Members")
        ordering = ['display_order', 'full_name']
    
    def __str__(self):
        return f"{self.full_name} - {self.get_position_display()}"
    
    @property
    def display_position(self):
        """Get display position (either choice or custom)"""
        if self.position == 'other' and self.custom_position:
            return self.custom_position
        return self.get_position_display()


class DealershipPhoto(models.Model):
    """
    Model to store dealership photos (showroom, facilities, etc.)
    """
    
    class PhotoTypeChoices(models.TextChoices):
        SHOWROOM = 'showroom', _('Showroom')
        FACILITY = 'facility', _('Facility')
        WORKSHOP = 'workshop', _('Workshop')
        EXTERIOR = 'exterior', _('Exterior')
        TEAM = 'team', _('Team')
        EVENT = 'event', _('Event')
        OTHER = 'other', _('Other')
    
    about_us = models.ForeignKey(
        AboutUs,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name=_("Dealership")
    )
    
    photo = models.ImageField(
        upload_to='dealership/photos/',
        verbose_name=_("Photo")
    )
    
    caption = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Caption")
    )
    
    photo_type = models.CharField(
        max_length=20,
        choices=PhotoTypeChoices.choices,
        default=PhotoTypeChoices.SHOWROOM,
        verbose_name=_("Photo Type")
    )
    
    display_order = models.IntegerField(
        default=0,
        verbose_name=_("Display Order")
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active")
    )
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Dealership Photo")
        verbose_name_plural = _("Dealership Photos")
        ordering = ['display_order', '-uploaded_at']
    
    def __str__(self):
        return f"{self.get_photo_type_display()} - {self.caption or 'No caption'}"        

class Event(models.Model):
    """Model for company events, conferences, webinars, and gatherings"""
    
    # Event status choices
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Event type choices
    TYPE_CHOICES = [
        ('conference', 'Conference'),
        ('webinar', 'Webinar'),
        ('workshop', 'Workshop'),
        ('meetup', 'Meetup'),
        ('trade_show', 'Trade Show'),
        ('product_launch', 'Product Launch'),
        ('press_event', 'Press Event'),
        ('networking', 'Networking Event'),
        ('training', 'Training Session'),
        ('virtual', 'Virtual Event'),
        ('hybrid', 'Hybrid Event'),
        ('other', 'Other'),
    ]
    
    # Basic information
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(max_length=500, help_text="Brief description for event listing")
    detailed_description = models.TextField()  # Use RichTextField for rich text if needed
    # detailed_description = RichTextField()  # Optional: install django-ckeditor
    
    # Event type and category
    event_type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        default='conference'
    )
    category = models.ForeignKey('EventCategory', on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField('EventTag', blank=True)
    
    # Date and time
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    timezone = models.CharField(
        max_length=100,
        default='UTC',
        help_text="Event timezone (e.g., 'America/New_York', 'UTC')"
    )
    
    # Location information
    is_virtual = models.BooleanField(default=False)
    venue_name = models.CharField(max_length=200, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    
    # Virtual event details
    virtual_platform = models.CharField(max_length=100, blank=True)
    virtual_link = models.URLField(blank=True)
    virtual_meeting_id = models.CharField(max_length=100, blank=True)
    virtual_passcode = models.CharField(max_length=100, blank=True)
    
    # Media
    cover_image = models.ImageField(
        upload_to='events/covers/',
        null=True,
        blank=True,
        help_text="Cover image for the event"
    )
    banner_image = models.ImageField(
        upload_to='events/banners/',
        null=True,
        blank=True,
        help_text="Banner image for event details page"
    )
    gallery = models.ManyToManyField('EventImage', blank=True, related_name="gallery")
    
    # Registration and capacity
    requires_registration = models.BooleanField(default=True)
    is_free = models.BooleanField(default=True)
    registration_link = models.URLField(blank=True)
    max_attendees = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)]
    )
    current_attendees = models.PositiveIntegerField(default=0)
    
    # Pricing (if not free)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Price per attendee",
        null=True,
        blank=True,
    )
    currency = models.CharField(max_length=3, default='ETB', null=True, blank=True)
    
    # Status and visibility
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    is_featured = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    
    # SEO and metadata
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(max_length=300, blank=True)
    meta_keywords = models.CharField(max_length=200, blank=True)
    
    # Organizer information
    organizer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='organized_events',
        blank=True
    )
    contact_person = models.CharField(max_length=200, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    views = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ['start_date', 'title']
        indexes = [
            models.Index(fields=['status', 'start_date']),
            models.Index(fields=['event_type']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['is_virtual']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Auto-generate slug from title if not provided
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Set published_at timestamp when status changes from draft
        if self.status != 'draft' and not self.published_at:
            self.published_at = timezone.now()
        
        # Update status based on dates
        self.update_status_based_on_dates()
        
        super().save(*args, **kwargs)
    
    def update_status_based_on_dates(self):
        """Update event status based on current date and event dates"""
        now = timezone.now()
        
        if self.status == 'cancelled':
            return
        
        if now < self.start_date:
            self.status = 'upcoming'
        elif self.start_date <= now <= self.end_date:
            self.status = 'ongoing'
        elif now > self.end_date:
            self.status = 'completed'
    
    def get_absolute_url(self):
        return reverse('event-detail', kwargs={'slug': self.slug})
    
    def increment_views(self):
        """Increment view count"""
        self.views += 1
        self.save(update_fields=['views'])
    
    @property
    def duration_days(self):
        """Calculate event duration in days"""
        if self.start_date and self.end_date:
            duration = self.end_date - self.start_date
            return duration.days + 1  # Inclusive count
        return None
    
    @property
    def is_upcoming(self):
        return self.status == 'upcoming'
    
    @property
    def is_ongoing(self):
        return self.status == 'ongoing'
    
    @property
    def is_completed(self):
        return self.status == 'completed'
    
    @property
    def registration_open(self):
        """Check if registration is still open"""
        if not self.requires_registration:
            return False
        
        if self.max_attendees and self.current_attendees >= self.max_attendees:
            return False
        
        if self.status in ['cancelled', 'completed']:
            return False
        
        # Allow registration until event starts
        return timezone.now() < self.start_date
    
    @property
    def seats_available(self):
        """Calculate available seats"""
        if self.max_attendees:
            return max(0, self.max_attendees - self.current_attendees)
        return None

class EventCategory(models.Model):
    """Categories for organizing events"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Font Awesome icon class (e.g., 'fa-calendar')"
    )
    color = models.CharField(
        max_length=7,
        default='#3B82F6',
        help_text="Hex color code for category"
    )
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = "Event Category"
        verbose_name_plural = "Event Categories"
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class EventTag(models.Model):
    """Tags for categorizing events"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class EventImage(models.Model):
    """Images for event gallery"""
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='event_images'
    )
    image = models.ImageField(upload_to='events/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    alt_text = models.CharField(max_length=200, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['display_order', 'uploaded_at']
    
    def __str__(self):
        return f"Image for {self.event.title}"

class EventSpeaker(models.Model):
    """Speakers for events"""
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='speakers'
    )
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200, blank=True)
    company = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(
        upload_to='events/speakers/',
        null=True,
        blank=True
    )
    twitter = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    website = models.URLField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.event.title}"

class EventSchedule(models.Model):
    """Schedule/agenda for events"""
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    day = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    speakers = models.ManyToManyField(EventSpeaker, blank=True)
    
    class Meta:
        ordering = ['day', 'start_time']
        verbose_name = "Event Schedule"
        verbose_name_plural = "Event Schedules"
    
    def __str__(self):
        return f"{self.title} - {self.day}"

class EventRegistration(models.Model):
    """Registrations for events"""
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='event_registrations'
    )
    registration_date = models.DateTimeField(auto_now_add=True)
    
    # Attendee information
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=200, blank=True)
    
    # Additional fields
    dietary_preferences = models.CharField(max_length=200, blank=True)
    special_requirements = models.TextField(blank=True)
    
    # Status
    is_confirmed = models.BooleanField(default=True)
    checked_in = models.BooleanField(default=False)
    checkin_time = models.DateTimeField(null=True, blank=True)
    
    # Payment information (if event is paid)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('refunded', 'Refunded'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )
    payment_reference = models.CharField(max_length=200, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    class Meta:
        unique_together = ['event', 'email']
        ordering = ['-registration_date']
    
    def __str__(self):
        return f"{self.full_name} - {self.event.title}"
    
    def save(self, *args, **kwargs):
        # Update event's current attendees count
        if self.is_confirmed and not self.pk:
            self.event.current_attendees += 1
            self.event.save(update_fields=['current_attendees'])
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Decrement event's current attendees count when deleting confirmed registration
        if self.is_confirmed:
            self.event.current_attendees = max(0, self.event.current_attendees - 1)
            self.event.save(update_fields=['current_attendees'])
        super().delete(*args, **kwargs)

class EventWaitlist(models.Model):
    """Waitlist for events that are full"""
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='waitlist'
    )
    email = models.EmailField()
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)
    notified_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['event', 'email']
        ordering = ['joined_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.event.title}"



class News(models.Model):
    """Simple News model with essential fields"""
    
    # Status choices
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    # Basic fields
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(help_text="Short description for news listing")
    content = models.TextField(help_text="Full news content")
    
    # Image field
    image = models.ImageField(
        upload_to='news/images/',
        null=True,
        blank=True,
        help_text="News image/thumbnail"
    )
    
    # Status and dates
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    is_featured = models.BooleanField(default=False)
    
    # Author and timestamps
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='news_articles'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "News"
        verbose_name_plural = "News"
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Auto-generate slug from title if not provided
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('news-detail', kwargs={'slug': self.slug})
    
    @property
    def is_published(self):
        return self.status == 'published' and self.published_at <= timezone.now()
    
    @property
    def formatted_published_date(self):
        if self.published_at:
            return self.published_at.strftime("%B %d, %Y")
        return None
    
    @property
    def excerpt(self):
        """Get first 150 characters as excerpt"""
        if len(self.description) > 150:
            return self.description[:150] + '...'
        return self.description        



class FinanceInformationPage(models.Model):
    """Main finance information page for users"""
    LAYOUT_CHOICES = [
        ('calculator', 'Calculator Focus'),
        ('offers', 'Offers Focus'),
        ('educational', 'Educational Focus'),
        ('comparison', 'Comparison Focus'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    subtitle = models.CharField(max_length=300, blank=True)
    
    # Content
    hero_title = models.CharField(max_length=200)
    hero_description = models.TextField()
    hero_image = models.ImageField(upload_to='finance/hero/', blank=True)
    
    # Features section
    features_title = models.CharField(max_length=200, default="Why Finance With Us?")
    features_intro = models.TextField(blank=True)
    
    # Calculator settings
    show_loan_calculator = models.BooleanField(default=True)
    show_lease_calculator = models.BooleanField(default=True)
    show_affordability_calculator = models.BooleanField(default=True)
    
    # Content sections
    faq_section_title = models.CharField(max_length=200, default="Frequently Asked Questions")
    offers_section_title = models.CharField(max_length=200, default="Current Finance Offers")
    
    # Display settings
    layout = models.CharField(max_length=20, choices=LAYOUT_CHOICES, default='calculator')
    display_order = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'title']
        verbose_name = "Finance Information Page"
        verbose_name_plural = "Finance Information Pages"
    
    def __str__(self):
        return self.title

class FinanceFeature(models.Model):
    """Features/benefits of financing with us"""
    page = models.ForeignKey(FinanceInformationPage, on_delete=models.CASCADE, related_name='features')
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="FontAwesome icon class or image filename")
    display_order = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['display_order']
    
    def __str__(self):
        return self.title

class FinanceFAQ(models.Model):
    """Frequently Asked Questions about financing"""
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('eligibility', 'Eligibility'),
        ('process', 'Application Process'),
        ('rates', 'Rates & Terms'),
        ('documents', 'Required Documents'),
        ('payment', 'Payments'),
    ]
    
    question = models.CharField(max_length=200)
    answer = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    display_order = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'display_order']
        verbose_name = "Finance FAQ"
        verbose_name_plural = "Finance FAQs"
    
    def __str__(self):
        return self.question
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class FinanceOffer(models.Model):
    """Special finance offers to display to users"""
    OFFER_TYPE_CHOICES = [
        ('low_apr', 'Low APR Offer'),
        ('cashback', 'Cashback Offer'),
        ('zero_down', 'Zero Down Payment'),
        ('special_lease', 'Special Lease Rate'),
        ('loyalty', 'Loyalty Bonus'),
        ('seasonal', 'Seasonal Offer'),
    ]
    
    title = models.CharField(max_length=200)
    short_description = models.CharField(max_length=100)
    full_description = models.TextField()
    
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES)
    badge_text = models.CharField(max_length=20, default="Special Offer")
    
    # Offer details
    apr_rate = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Annual Percentage Rate"
    )
    cashback_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Cashback amount if applicable"
    )
    down_payment_percent = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Minimum down payment percentage"
    )
    term_months = models.IntegerField(
        null=True, 
        blank=True,
        help_text="Loan term in months"
    )
    
    # Eligibility
    eligibility_requirements = models.TextField(blank=True)
    min_credit_score = models.IntegerField(default=600, null=True, blank=True)
    
    # Validity
    valid_from = models.DateField()
    valid_until = models.DateField()
    is_active = models.BooleanField(default=True)
    
    # Display
    featured_image = models.ImageField(upload_to='finance/offers/', blank=True)
    display_color = models.CharField(max_length=7, default="#3B82F6", help_text="Hex color for offer card")
    display_priority = models.IntegerField(default=1, help_text="1 = highest priority")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_priority', '-valid_from']
    
    def __str__(self):
        return self.title
    
    def clean(self):
        """Validate the offer dates"""
        super().clean()
        
        # Validate dates if both are provided
        if self.valid_from and self.valid_until:
            if self.valid_from > self.valid_until:
                raise ValidationError({
                    'valid_until': 'Valid until date must be after valid from date.'
                })
    
    def save(self, *args, **kwargs):
        """Run validation before saving"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def is_current(self):
        """
        Check if offer is currently valid.
        Returns False if dates are not set or invalid.
        """
        # Early return if dates are not set
        if self.valid_from is None or self.valid_until is None:
            return False
        
        today = timezone.now().date()
        
        try:
            # Ensure both are date objects before comparison
            return self.valid_from <= today <= self.valid_until
        except (TypeError, AttributeError):
            # Handle any unexpected errors
            return False
    
    @property
    def days_remaining(self):
        """Calculate days remaining for the offer"""
        if not self.is_current:
            return 0
        
        today = timezone.now().date()
        if self.valid_until:
            delta = self.valid_until - today
            return max(0, delta.days)
        return 0
class FinanceCalculator(models.Model):
    """Pre-configured calculator examples"""
    CALCULATOR_TYPE_CHOICES = [
        ('loan', 'Loan Calculator'),
        ('lease', 'Lease Calculator'),
        ('affordability', 'Affordability Calculator'),
        ('comparison', 'Loan Comparison'),
    ]
    
    title = models.CharField(max_length=200)
    calculator_type = models.CharField(max_length=20, choices=CALCULATOR_TYPE_CHOICES)
    description = models.TextField(blank=True)
    
    # Example parameters
    example_loan_amount = models.DecimalField(max_digits=10, decimal_places=2, default=30000.00)
    example_interest_rate = models.DecimalField(max_digits=4, decimal_places=2, default=5.99)
    example_term_months = models.IntegerField(default=60)
    example_down_payment = models.DecimalField(max_digits=10, decimal_places=2, default=3000.00)
    
    # Results
    example_monthly_payment = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    example_total_interest = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    example_total_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=1)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Auto-calculate example payment
        if not self.example_monthly_payment and self.calculator_type == 'loan':
            # Simple monthly payment calculation
            monthly_rate = self.example_interest_rate / 100 / 12
            loan_amount = self.example_loan_amount - self.example_down_payment
            n = self.example_term_months
            
            if monthly_rate > 0:
                monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** n) / ((1 + monthly_rate) ** n - 1)
            else:
                monthly_payment = loan_amount / n
                
            self.example_monthly_payment = round(monthly_payment, 2)
            self.example_total_cost = round(monthly_payment * n + self.example_down_payment, 2)
            self.example_total_interest = round(monthly_payment * n - loan_amount, 2)
        
        super().save(*args, **kwargs)

class FinanceDocument(models.Model):
    """Documents/info required for financing"""
    DOCUMENT_TYPE_CHOICES = [
        ('required', 'Required Document'),
        ('helpful', 'Helpful Document'),
        ('form', 'Application Form'),
        ('guide', 'Guide/FAQ'),
    ]
    
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    description = models.TextField()
    
    file = models.FileField(upload_to='finance/documents/', blank=True)
    external_url = models.URLField(blank=True)
    
    icon = models.CharField(max_length=50, help_text="FontAwesome icon class", default='fas fa-file')
    display_order = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['document_type', 'display_order']
    
    def __str__(self):
        return self.title

class FinancePartner(models.Model):
    """Our finance partners/banks"""
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='finance/partners/')
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    
    # Partner offerings
    min_apr = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    max_apr = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    special_features = models.TextField(blank=True)
    
    display_order = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['display_order']
    
    def __str__(self):
        return self.name


class ServiceCategory(models.Model):
    """Service categories for grouping services"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    icon = models.CharField(
        max_length=50,
        help_text="FontAwesome icon class (e.g., fas fa-shield-alt)"
    )
    icon_color = models.CharField(
        max_length=20,
        default="#3B82F6",
        help_text="Hex color for icon background"
    )
    display_order = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Service Category"
        verbose_name_plural = "Service Categories"
        ordering = ['display_order', 'title']
    
    def __str__(self):
        return self.title

class Service(models.Model):
    """Main service offering model"""
    SERVICE_TYPE_CHOICES = [
        ('warranty', 'Warranty Service'),
        ('maintenance', 'Maintenance Service'),
        ('repair', 'Repair Service'),
        ('inspection', 'Vehicle Inspection'),
        ('installation', 'Accessory Installation'),
        ('emergency', 'Emergency Service'),
        ('consultation', 'Consultation Service'),
    ]
    
    DURATION_UNIT_CHOICES = [
        ('months', 'Months'),
        ('years', 'Years'),
        ('days', 'Days'),
        ('hours', 'Hours'),
        ('lifetime', 'Lifetime'),
        ('unlimited', 'Unlimited'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    short_description = models.CharField(max_length=200)
    full_description = models.TextField()
    
    # Category and Type
    category = models.ForeignKey(
        ServiceCategory, 
        on_delete=models.CASCADE, 
        related_name='services',
        null=True,
        blank=True
    )
    service_type = models.CharField(
        max_length=20, 
        choices=SERVICE_TYPE_CHOICES,
        default='maintenance'
    )
    
    # Pricing and Duration
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Price in ETB"
    )
    price_display = models.CharField(
        max_length=100,
        default='Contact for pricing',
        help_text="How price appears (e.g., 'Free', 'From 5,000 ETB')"
    )
    duration_value = models.IntegerField(
        default=1,
        help_text="Duration number (e.g., 2 for 2 years)"
    )
    duration_unit = models.CharField(
        max_length=10,
        choices=DURATION_UNIT_CHOICES,
        default='months'
    )
    
    # Special Offers
    is_special_offer = models.BooleanField(default=False)
    special_offer_text = models.CharField(max_length=100, blank=True)
    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    
    # Eligibility - Updated to use ElectricCar
    eligibility_description = models.TextField(blank=True)
    eligible_car_models = models.ManyToManyField(
        'etop_backend.ElectricCar',  
        related_name='eligible_services',
        blank=True,
        help_text="Specific electric car models eligible for this service"
    )
    eligible_manufacturers = models.ManyToManyField(
        'etop_backend.Manufacturer',  
        related_name='eligible_services',
        blank=True,
        help_text="Manufacturers eligible for this service"
    )
    min_vehicle_year = models.IntegerField(
        null=True,
        blank=True,
        help_text="Minimum vehicle year eligible"
    )
    max_vehicle_year = models.IntegerField(
        null=True,
        blank=True,
        help_text="Maximum vehicle year eligible"
    )
    
    # Special NETA Battery Warranty flag
    is_neta_battery_warranty = models.BooleanField(
        default=False,
        help_text="Special 2-year battery warranty for NETA cars only"
    )
    
    # Features
    features = models.JSONField(
        default=list,
        blank=True,
        help_text="List of features as JSON array"
    )
    
    # Service Details
    service_center_required = models.BooleanField(default=True)
    mobile_service_available = models.BooleanField(default=False)
    appointment_required = models.BooleanField(default=True)
    estimated_service_time = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., '2-3 hours', '1 day'"
    )
    
    # First Round Service flag
    is_first_round_service = models.BooleanField(
        default=False,
        help_text="First round service for all cars"
    )
    
    # Warranty Specific
    warranty_coverage = models.TextField(blank=True)
    warranty_exclusions = models.TextField(blank=True)
    warranty_claim_process = models.TextField(blank=True)
    
    # Images
    featured_image = models.ImageField(
        upload_to='services/featured/',
        blank=True
    )
    brochure = models.FileField(
        upload_to='services/brochures/',
        blank=True,
        null=True
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    display_order = models.IntegerField(default=1)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'title']
        verbose_name = "Service"
        verbose_name_plural = "Services"
    
    def __str__(self):
        return self.title
    
    @property
    def display_duration(self):
        """Formatted duration display"""
        if self.duration_unit == 'lifetime':
            return 'Lifetime'
        elif self.duration_unit == 'unlimited':
            return 'Unlimited'
        else:
            unit_display = {
                'months': 'Month' if self.duration_value == 1 else 'Months',
                'years': 'Year' if self.duration_value == 1 else 'Years',
                'days': 'Day' if self.duration_value == 1 else 'Days',
                'hours': 'Hour' if self.duration_value == 1 else 'Hours',
            }
            return f"{self.duration_value} {unit_display.get(self.duration_unit, self.duration_unit)}"
    
    @property
    def is_current_special(self):
        """Check if special offer is currently valid"""
        from django.utils import timezone
        
        if not self.is_special_offer:
            return False
        
        today = timezone.now().date()
        
        if self.valid_from and self.valid_until:
            return self.valid_from <= today <= self.valid_until
        elif self.valid_from:
            return self.valid_from <= today
        
        return True
    
    @property
    def days_remaining(self):
        """Days remaining for special offer"""
        from django.utils import timezone
        
        if not self.is_current_special or not self.valid_until:
            return None
        
        today = timezone.now().date()
        delta = self.valid_until - today
        return max(0, delta.days)
    
    @property
    def is_neta_exclusive(self):
        """Check if this is NETA exclusive service"""
        return self.is_neta_battery_warranty
    
    @property
    def is_universal_service(self):
        """Check if this service is for all cars"""
        return self.is_first_round_service

class ServicePackage(models.Model):
    """Pre-configured service packages"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    
    # Package details
    services = models.ManyToManyField(
        Service,
        related_name='packages',
        help_text="Services included in this package"
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Discounted package price"
    )
    individual_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total price if services purchased individually"
    )
    
    # Savings
    savings_percentage = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage savings"
    )
    savings_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Amount saved in ETB"
    )
    
    # Target audience
    recommended_for = models.CharField(
        max_length=200,
        blank=True,
        help_text="e.g., 'New EV Owners', 'High Mileage Vehicles'"
    )
    
    # Display
    badge_text = models.CharField(max_length=50, default='Best Value')
    display_color = models.CharField(max_length=7, default="#10B981")
    display_order = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order']
    
    def __str__(self):
        return self.title
    
    @property
    def display_savings(self):
        return f"Save {self.savings_percentage}% (ETB {self.savings_amount})"

class ServiceFAQ(models.Model):
    """Frequently Asked Questions about services"""
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('warranty', 'Warranty'),
        ('maintenance', 'Maintenance'),
        ('pricing', 'Pricing'),
        ('process', 'Service Process'),
        ('eligibility', 'Eligibility'),
    ]
    
    question = models.CharField(max_length=200)
    answer = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='general'
    )
    related_service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='faqs'
    )
    
    display_order = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'display_order']
        verbose_name = "Service FAQ"
        verbose_name_plural = "Service FAQs"
    
    def __str__(self):
        return self.question

class ServiceTestimonial(models.Model):
    """Customer testimonials for services"""
    RATING_CHOICES = [
        (1, '★☆☆☆☆'),
        (2, '★★☆☆☆'),
        (3, '★★★☆☆'),
        (4, '★★★★☆'),
        (5, '★★★★★'),
    ]
    
    customer_name = models.CharField(max_length=100)
    customer_vehicle = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., 'Tesla Model 3', 'NETA V'"
    )
    service_received = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='testimonials'
    )
    testimonial = models.TextField()
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    
    # Optional fields
    customer_location = models.CharField(max_length=100, blank=True)
    service_date = models.DateField(null=True, blank=True)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Display
    featured_image = models.ImageField(
        upload_to='services/testimonials/',
        blank=True
    )
    display_order = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-service_date', 'display_order']
    
    def __str__(self):
        return f"{self.customer_name} - {self.service_received.title}"

class ServiceCenter(models.Model):
    """Service center locations"""
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    
    # Coordinates
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6,
        null=True,
        blank=True
    )
    
    # Services offered
    services_offered = models.ManyToManyField(
        Service,
        related_name='service_centers',
        blank=True
    )
    
    # Hours
    opening_hours = models.JSONField(
        default=dict,
        help_text="JSON with day:hours pairs"
    )
    
    # Facilities
    has_ev_charging = models.BooleanField(default=True)
    has_waiting_lounge = models.BooleanField(default=True)
    has_loaner_cars = models.BooleanField(default=False)
    has_mobile_service = models.BooleanField(default=False)
    
    # Status
    is_main_center = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_main_center', 'city', 'name']
    
    def __str__(self):
        return f"{self.name}, {self.city}"