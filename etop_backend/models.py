# models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from decimal import Decimal
from django.core.validators import EmailValidator  
from django.core.exceptions import ValidationError  



class Manufacturer(models.Model):
    """Electric vehicle manufacturer"""
    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=100)
    founded_year = models.IntegerField(null=True, blank=True)
    is_ev_only = models.BooleanField(default=False, verbose_name="EV Only Manufacturer")
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='manufacturer_logos/', null=True, blank=True)
    website = models.URLField(blank=True)
    headquarters = models.CharField(max_length=200, blank=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Manufacturer"
        verbose_name_plural = "Manufacturers"
        
    def __str__(self):
        return self.name


class CarColor(models.Model):
    """Car color options for interior and exterior"""
    COLOR_TYPE_CHOICES = [
        ("exterior", "Exterior Color"),
        ("interior", "Interior Color"),
    ]

    name = models.CharField(max_length=50)
    hex_code = models.CharField(max_length=7, blank=True, null=True, help_text="#RRGGBB format")
    color_type = models.CharField(max_length=20, choices=COLOR_TYPE_CHOICES)
    image = models.ImageField(upload_to="car_colors/", blank=True, null=True, help_text="Color swatch/preview")
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['color_type', 'name']
        verbose_name = "Car Color"
        verbose_name_plural = "Car Colors"

    def __str__(self):
        return f"{self.name} ({self.color_type})"


class ElectricCar(models.Model):
    """Electric Vehicle Model"""
    
    CHARGING_TYPE_CHOICES = [
        ('type1', 'Type 1 (SAE J1772)'),
        ('type2', 'Type 2 (Mennekes)'),
        ('ccs1', 'CCS1 (Combo 1)'),
        ('ccs2', 'CCS2 (Combo 2)'),
        ('chademo', 'CHAdeMO'),
        ('tesla', 'Tesla Supercharger'),
        ('gb_t', 'GB/T (China)'),
        ('nacs', 'NACS (Tesla Standard)'),
    ]
    
    BATTERY_TYPE_CHOICES = [
        ('lithium_ion', 'Lithium-Ion'),
        ('lithium_polymer', 'Lithium Polymer'),
        ('solid_state', 'Solid State'),
        ('lifepo4', 'Lithium Iron Phosphate (LiFePO4)'),
        ('nmc', 'NMC (Nickel Manganese Cobalt)'),
        ('lto', 'LTO (Lithium Titanate)'),
    ]
    
    DRIVE_TYPE_CHOICES = [
        ('rwd', 'Rear Wheel Drive'),
        ('fwd', 'Front Wheel Drive'),
        ('awd', 'All Wheel Drive'),
        ('dual_motor', 'Dual Motor AWD'),
        ('tri_motor', 'Tri Motor AWD'),
        ('quad_motor', 'Quad Motor AWD'),
    ]
    
    CATEGORY_CHOICES = [
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('crossover', 'Crossover'),
        ('hatchback', 'Hatchback'),
        ('coupe', 'Coupe'),
        ('convertible', 'Convertible'),
        ('sports', 'Sports Car'),
        ('pickup', 'Pickup Truck'),
        ('van', 'Van/Minibus'),
        ('luxury', 'Luxury'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available for Sale'),
        ('reserved', 'Reserved'),
        ('sold', 'Sold'),
        ('test_drive', 'Available for Test Drive'),
        ('coming_soon', 'Coming Soon'),
        ('pre_order', 'Pre-order Available'),
        ('display', 'Display Model Only'),
    ]
    
    # Basic Information
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, related_name='electric_cars')
    model_name = models.CharField(max_length=100)
    variant = models.CharField(max_length=100, blank=True, help_text="e.g., Long Range, Performance, Standard")
    model_year = models.IntegerField(
        validators=[MinValueValidator(2008), MaxValueValidator(2025)]
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    featured = models.BooleanField(default=False, help_text="Featured on homepage")
    
    # Battery Information
    battery_capacity = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        help_text="Total battery capacity in kWh"
    )
    usable_battery = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Usable battery capacity in kWh"
    )
    battery_type = models.CharField(max_length=20, choices=BATTERY_TYPE_CHOICES, default='lithium_ion')
    battery_warranty_years = models.IntegerField(default=8)
    battery_warranty_km = models.IntegerField(default=160000, help_text="Warranty in kilometers")
    
    # Range & Efficiency
    range_wltp = models.IntegerField(help_text="WLTP range in km", verbose_name="WLTP Range")
    range_epa = models.IntegerField(
        help_text="EPA estimated range in km",
        null=True,
        blank=True,
        verbose_name="EPA Range"
    )
    energy_consumption = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Energy consumption in kWh/100km",
        null=True,
        blank=True
    )
    
    # Performance
    acceleration_0_100 = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        help_text="0-100 km/h acceleration in seconds"
    )
    top_speed = models.IntegerField(help_text="Top speed in km/h")
    motor_power = models.IntegerField(help_text="Total motor power in kW")
    torque = models.IntegerField(help_text="Torque in Nm")
    drive_type = models.CharField(max_length=20, choices=DRIVE_TYPE_CHOICES)
    
    # Charging
    max_dc_charging = models.IntegerField(
        help_text="Maximum DC charging power in kW",
        verbose_name="Max DC Charging"
    )
    max_ac_charging = models.IntegerField(
        help_text="Maximum AC charging power in kW",
        verbose_name="Max AC Charging"
    )
    charging_type = models.CharField(
        max_length=20,
        choices=CHARGING_TYPE_CHOICES,
        default='ccs2'
    )
    charging_time_10_80 = models.IntegerField(
        help_text="Time to charge from 10% to 80% at max DC power (minutes)"
    )
    charging_time_0_100_ac = models.IntegerField(
        help_text="Time for 0-100% on 11kW AC charger (hours)",
        null=True,
        blank=True
    )
    
    # Dimensions & Capacity
    length = models.IntegerField(help_text="Length in mm")
    width = models.IntegerField(help_text="Width in mm")
    height = models.IntegerField(help_text="Height in mm")
    wheelbase = models.IntegerField(help_text="Wheelbase in mm", null=True, blank=True)
    curb_weight = models.IntegerField(help_text="Curb weight in kg")
    cargo_capacity = models.IntegerField(help_text="Cargo capacity in liters")
    seating_capacity = models.IntegerField(default=5)
    
    # Color Options
    available_exterior_colors = models.ManyToManyField(
        CarColor, 
        related_name="available_exterior_cars", 
        limit_choices_to={"color_type": "exterior"},
        blank=True,
        help_text="Available exterior color options"
    )
    
    available_interior_colors = models.ManyToManyField(
        CarColor, 
        related_name="available_interior_cars", 
        limit_choices_to={"color_type": "interior"},
        blank=True,
        help_text="Available interior color options"
    )
    
    # Features & Technology
    has_heat_pump = models.BooleanField(default=False)
    has_battery_preconditioning = models.BooleanField(default=False)
    has_v2l = models.BooleanField(
        default=False,
        verbose_name="Vehicle-to-Load",
        help_text="Can power external devices"
    )
    has_v2g = models.BooleanField(
        default=False,
        verbose_name="Vehicle-to-Grid",
        help_text="Can supply power back to grid"
    )
    has_one_pedal_driving = models.BooleanField(default=False)
    regen_braking_levels = models.IntegerField(
        default=1,
        help_text="Number of regenerative braking levels"
    )
    autopilot_level = models.CharField(
        max_length=50,
        choices=[
            ('none', 'No Autopilot'),
            ('basic', 'Basic Driver Assistance'),
            ('level2', 'Level 2 Autonomy'),
            ('level3', 'Level 3 Autonomy'),
            ('level4', 'Level 4 Autonomy'),
        ],
        default='basic'
    )
    charging_port_location = models.CharField(
        max_length=50,
        choices=[
            ('front_left', 'Front Left'),
            ('front_right', 'Front Right'),
            ('rear_left', 'Rear Left'),
            ('rear_right', 'Rear Right'),
            ('front', 'Front Center'),
            ('rear', 'Rear Center'),
        ],
        default='rear_left'
    )
    
    # Pricing
    base_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Base price in ETB"
    )
    estimated_delivery = models.CharField(
        max_length=100,
        blank=True,
        help_text="Estimated delivery time"
    )
    tax_incentive = models.BooleanField(
        default=False,
        help_text="Eligible for government tax incentives"
    )
    
    # Main Images
    main_image = models.ImageField(upload_to='electric_cars/main/', null=True, blank=True)
    brochure = models.FileField(
        upload_to='electric_cars/brochures/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(['pdf'])]
    )
    
    # Description
    description = models.TextField()
    key_features = models.TextField(help_text="List key features separated by commas")
    safety_features = models.TextField(blank=True, help_text="Safety features")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='evs_created')
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    
    class Meta:
        ordering = ['manufacturer', 'model_name', 'model_year']
        unique_together = ['manufacturer', 'model_name', 'variant', 'model_year']
        verbose_name = "Electric Car"
        verbose_name_plural = "Electric Cars"
    
    def __str__(self):
        return f"{self.manufacturer.name} {self.model_name} {self.variant} ({self.model_year})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.manufacturer.name} {self.model_name} {self.variant} {self.model_year}")
            self.slug = base_slug[:200]
        super().save(*args, **kwargs)
    
    @property
    def display_name(self):
        if self.variant:
            return f"{self.manufacturer.name} {self.model_name} {self.variant}"
        return f"{self.manufacturer.name} {self.model_name}"
    
    @property
    def efficiency(self):
        """Calculate efficiency in km/kWh"""
        if self.range_wltp and self.battery_capacity:
            return round(float(self.range_wltp) / float(self.battery_capacity), 2)
        return None
    
    @property
    def charging_speed(self):
        """Calculate charging speed in km per minute"""
        if self.max_dc_charging and self.efficiency:
            return round((self.max_dc_charging * self.efficiency) / 60, 2)
        return None
    
    @property
    def is_available_for_sale(self):
        return self.status in ['available', 'pre_order', 'coming_soon']
    
    @property
    def default_exterior_color(self):
        """Get first available exterior color"""
        return self.available_exterior_colors.first()
    
    @property
    def default_interior_color(self):
        """Get first available interior color"""
        return self.available_interior_colors.first()


class CarColorImage(models.Model):
    """Images showing specific color combinations of cars"""
    IMAGE_TYPE_CHOICES = [
        ('exterior', 'Exterior View'),
        ('interior', 'Interior View'),
        ('angle', 'Angle View'),
        ('detail', 'Detail Shot'),
        ('color_swatch', 'Color Swatch'),
    ]
    
    car = models.ForeignKey(ElectricCar, on_delete=models.CASCADE, related_name="color_images")
    exterior_color = models.ForeignKey(
        CarColor, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        limit_choices_to={"color_type": "exterior"},
        related_name="exterior_car_images"
    )
    
    interior_color = models.ForeignKey(
        CarColor, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        limit_choices_to={"color_type": "interior"},
        related_name="interior_car_images"
    )
    
    image = models.ImageField(upload_to="car_color_images/")
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPE_CHOICES, default='exterior')
    description = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False, help_text="Primary image for this color combination")
    order = models.IntegerField(default=0, help_text="Order for display")
    
    class Meta:
        ordering = ['order', '-is_primary']
        unique_together = ("car", "exterior_color", "interior_color", "image_type")
        verbose_name = "Car Color Image"
        verbose_name_plural = "Car Color Images"

    def __str__(self):
        parts = [self.car.display_name]
        if self.exterior_color:
            parts.append(f"Exterior: {self.exterior_color.name}")
        if self.interior_color:
            parts.append(f"Interior: {self.interior_color.name}")
        return " | ".join(parts)
    
    def save(self, *args, **kwargs):
        # Ensure only one primary image per color combination
        if self.is_primary:
            CarColorImage.objects.filter(
                car=self.car,
                exterior_color=self.exterior_color,
                interior_color=self.interior_color,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class CarColorConfiguration(models.Model):
    """Pre-configured color combinations with pricing"""
    car = models.ForeignKey(ElectricCar, on_delete=models.CASCADE, related_name="color_configurations")
    exterior_color = models.ForeignKey(
        CarColor, 
        on_delete=models.CASCADE,
        related_name="exterior_configurations",  
        limit_choices_to={"color_type": "exterior"}
    )
    
    interior_color = models.ForeignKey(
        CarColor, 
        on_delete=models.CASCADE,
        related_name="interior_configurations",  
        limit_choices_to={"color_type": "interior"}
    )
    
    price_adjustment = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Additional cost for this color combination (can be negative)"
    )
    is_popular = models.BooleanField(default=False, help_text="Popular color combination")
    is_available = models.BooleanField(default=True)
    delivery_time = models.CharField(
        max_length=50, 
        blank=True, 
        help_text="Special delivery time for this combination"
    )
    
    class Meta:
        ordering = ['-is_popular', 'price_adjustment']
        unique_together = ("car", "exterior_color", "interior_color")
        verbose_name = "Car Color Configuration"
        verbose_name_plural = "Car Color Configurations"
    
    def __str__(self):
        return f"{self.car.display_name} - {self.exterior_color.name}/{self.interior_color.name}"
    
    @property
    def total_price(self):
        """Calculate total price including color adjustments"""
        return self.car.base_price + self.price_adjustment
    
    @property
    def primary_image(self):
        """Get primary image for this color configuration"""
        return CarColorImage.objects.filter(
            car=self.car,
            exterior_color=self.exterior_color,
            interior_color=self.interior_color,
            is_primary=True
        ).first()
    
    @property
    def all_images(self):
        """Get all images for this color configuration"""
        return CarColorImage.objects.filter(
            car=self.car,
            exterior_color=self.exterior_color,
            interior_color=self.interior_color
        ).order_by('order')


class EVReview(models.Model):
    """Reviews for electric vehicles"""
    car = models.ForeignKey(ElectricCar, on_delete=models.CASCADE, related_name='reviews')
    reviewer_name = models.CharField(max_length=100)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review_text = models.TextField()
    pros = models.TextField(help_text="Separate pros with commas")
    cons = models.TextField(help_text="Separate cons with commas")
    verified_owner = models.BooleanField(default=False)
    review_date = models.DateField(auto_now_add=True)
    
    class Meta:
        ordering = ['-review_date']
    
    def __str__(self):
        return f"Review for {self.car} by {self.reviewer_name}"


class ChargingSpecification(models.Model):
    """Detailed charging specifications"""
    car = models.OneToOneField(ElectricCar, on_delete=models.CASCADE, related_name='charging_specs')
    
    # Charging Ports
    has_dc_port = models.BooleanField(default=True)
    has_ac_port = models.BooleanField(default=True)
    
    # Charging Times
    time_10_80_dc = models.IntegerField(help_text="Minutes for 10-80% on DC fast charger")
    time_0_100_ac_11kw = models.IntegerField(
        help_text="Hours for 0-100% on 11kW AC charger",
        null=True,
        blank=True
    )
    time_0_100_ac_7kw = models.IntegerField(
        help_text="Hours for 0-100% on 7kW AC charger",
        null=True,
        blank=True
    )
    
    # Battery Management
    battery_warranty_years = models.IntegerField(default=8)
    battery_warranty_miles = models.IntegerField(default=100000)
    battery_thermal_management = models.CharField(
        max_length=50,
        choices=[
            ('liquid', 'Liquid Cooling'),
            ('air', 'Air Cooling'),
            ('passive', 'Passive Cooling'),
            ('hybrid', 'Hybrid Cooling'),
        ]
    )
    
    class Meta:
        verbose_name = "Charging Specification"
        verbose_name_plural = "Charging Specifications"
    
    def __str__(self):
        return f"Charging specs for {self.car}"


class EVComparison(models.Model):
    """Comparison between electric vehicles"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    cars = models.ManyToManyField(ElectricCar, related_name='comparisons')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class EmailSubscriber(models.Model):
    """
    Model to store email subscribers.
    Sales associates will be selected from admin users.
    """
    
    class SubscriptionStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        UNSUBSCRIBED = 'unsubscribed', 'Unsubscribed'
        BOUNCED = 'bounced', 'Bounced'
        COMPLAINT = 'complaint', 'Marked as Spam'
    
    # Required fields
    email = models.EmailField(
        max_length=255, 
        unique=True,
        verbose_name="Email Address",
        help_text="Subscriber's email address"
    )
    
    # Optional fields
    first_name = models.CharField(max_length=100, blank=True, verbose_name="First Name")
    last_name = models.CharField(max_length=100, blank=True, verbose_name="Last Name")
    
    # Sales associate association - will be selected from User model (admin users)
    # Only users with staff/admin privileges can be selected
    sales_associate = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'is_staff': True},  # Only staff/admin users
        related_name='email_subscribers',
        verbose_name="Sales Associate",
        help_text="Select sales associate if customer was referred by one"
    )
    
    # Subscription details
    subscription_status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.ACTIVE,
        verbose_name="Subscription Status"
    )
    
    # Preferences
    receive_inventory_alerts = models.BooleanField(
        default=True,
        verbose_name="Receive Inventory Alerts",
        help_text="Send emails when new inventory is added"
    )
    
    # Timestamps
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name="Subscription Date")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Updated")
    unsubscribed_at = models.DateTimeField(blank=True, null=True, verbose_name="Unsubscribed Date")
    
    # Notes for admin reference
    notes = models.TextField(blank=True, verbose_name="Admin Notes")
    
    class Meta:
        verbose_name = "Email Subscriber"
        verbose_name_plural = "Email Subscribers"
        ordering = ['-subscribed_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['subscription_status']),
            models.Index(fields=['subscribed_at']),
            models.Index(fields=['sales_associate']),
        ]
    
    def __str__(self):
        name = f"{self.first_name} {self.last_name}".strip()
        if name:
            return f"{name} ({self.email})"
        return self.email
    
    def clean(self):
        """Custom validation"""
        # Email validation
        validator = EmailValidator()
        try:
            validator(self.email)
        except ValidationError:
            raise ValidationError({'email': 'Please enter a valid email address'})
        
        # Ensure email is lowercase
        self.email = self.email.lower()
    
    def save(self, *args, **kwargs):
        self.full_clean()  # Run validation before saving
        super().save(*args, **kwargs)
    
    def unsubscribe(self):
        """Mark subscriber as unsubscribed"""
        from django.utils import timezone
        self.subscription_status = self.SubscriptionStatus.UNSUBSCRIBED
        self.receive_inventory_alerts = False
        self.unsubscribed_at = timezone.now()
        self.save()
    
    def resubscribe(self):
        """Reactivate a subscriber"""
        self.subscription_status = self.SubscriptionStatus.ACTIVE
        self.receive_inventory_alerts = True
        self.unsubscribed_at = None
        self.save()
    
    @property
    def full_name(self):
        """Get subscriber's full name"""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_active_subscriber(self):
        """Check if subscriber is active and wants inventory alerts"""
        return (
            self.subscription_status == self.SubscriptionStatus.ACTIVE and 
            self.receive_inventory_alerts
        )
    
    @classmethod
    def get_active_subscribers(cls):
        """Get all active subscribers who want inventory alerts"""
        return cls.objects.filter(
            subscription_status=cls.SubscriptionStatus.ACTIVE,
            receive_inventory_alerts=True
        )
    
    @classmethod
    def get_subscribers_by_associate(cls, user_id):
        """Get all subscribers for a specific sales associate"""
        return cls.objects.filter(sales_associate_id=user_id)        


# models.py
from django.db import models
from django.core.validators import URLValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
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