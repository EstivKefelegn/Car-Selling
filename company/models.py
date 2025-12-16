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