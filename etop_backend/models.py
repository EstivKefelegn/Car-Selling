# models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from decimal import Decimal
from django.core.validators import EmailValidator  
from django.core.exceptions import ValidationError  
from django.db.models import Q
import uuid



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


def generate_booking_number():
    """Generate unique booking number"""
    return f"SRV{timezone.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"

class CustomerVehicle(models.Model):
    """Customer's vehicle information for service booking"""
    VEHICLE_SOURCE_CHOICES = [
        ('our_dealership', 'Purchased from Our Dealership'),
        ('other_dealership', 'Purchased from Other Dealership'),
        ('private_sale', 'Private Sale'),
        ('company_fleet', 'Company Fleet'),
        ('rental', 'Rental Vehicle'),
        ('other', 'Other'),
    ]
    
    customer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='customer_vehicles'
    )
    
    # Link to ElectricCar model if it's one of our models
    electric_car = models.ForeignKey(
        'ElectricCar',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customer_vehicles',
        help_text="If this is one of our electric car models"
    )
    
    # Custom vehicle details (if not in ElectricCar)
    custom_make = models.CharField(max_length=100, blank=True)
    custom_model = models.CharField(max_length=100, blank=True)
    custom_year = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1900), MaxValueValidator(2025)]
    )
    
    # Vehicle identification
    license_plate = models.CharField(max_length=20)
    vin = models.CharField(
        max_length=17, 
        verbose_name="Vehicle Identification Number"
    )
    color = models.CharField(max_length=50, blank=True)
    
    # Purchase information
    source = models.CharField(
        max_length=20, 
        choices=VEHICLE_SOURCE_CHOICES,
        default='our_dealership'
    )
    purchased_from_us = models.BooleanField(default=False)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_odometer = models.IntegerField(
        null=True, 
        blank=True,
        help_text="Odometer reading at purchase (km)"
    )
    sales_invoice_number = models.CharField(max_length=100, blank=True)
    
    # Current status
    current_odometer = models.IntegerField(
        help_text="Current odometer reading in kilometers"
    )
    last_service_date = models.DateField(null=True, blank=True)
    last_service_odometer = models.IntegerField(null=True, blank=True)
    last_service_type = models.CharField(max_length=100, blank=True)
    
    # Warranty information
    has_warranty = models.BooleanField(default=False)
    warranty_start_date = models.DateField(null=True, blank=True)
    warranty_end_date = models.DateField(null=True, blank=True)
    warranty_type = models.CharField(max_length=100, blank=True)
    warranty_terms = models.TextField(blank=True)
    
    # NETA specific warranty
    is_neta_car = models.BooleanField(default=False)
    neta_battery_warranty_years = models.IntegerField(
        default=2,
        help_text="NETA battery warranty years"
    )
    neta_battery_warranty_km = models.IntegerField(
        default=50000,
        help_text="NETA battery warranty kilometers"
    )
    
    # 10,000 KM service eligibility
    is_eligible_for_10000km_service = models.BooleanField(default=False)
    next_service_due_km = models.IntegerField(
        null=True,
        blank=True,
        help_text="Next service due at this kilometer reading"
    )
    next_service_due_date = models.DateField(
        null=True,
        blank=True,
        help_text="Next service due date"
    )
    
    # Additional information
    additional_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Customer Vehicle"
        verbose_name_plural = "Customer Vehicles"
        unique_together = ['license_plate', 'vin']
    
    def __str__(self):
        if self.electric_car:
            return f"{self.electric_car.display_name} - {self.license_plate}"
        return f"{self.custom_make} {self.custom_model} ({self.custom_year}) - {self.license_plate}"
    
    @property
    def make(self):
        """Get make from electric_car or custom_make"""
        if self.electric_car:
            return self.electric_car.manufacturer.name
        return self.custom_make
    
    @property
    def model(self):
        """Get model from electric_car or custom_model"""
        if self.electric_car:
            return self.electric_car.model_name
        return self.custom_model
    
    @property
    def year(self):
        """Get year from electric_car or custom_year"""
        if self.electric_car:
            return self.electric_car.model_year
        return self.custom_year
    
    @property
    def display_name(self):
        """Display vehicle name"""
        if self.electric_car:
            return f"{self.electric_car.display_name} - {self.license_plate}"
        return f"{self.custom_make} {self.custom_model} ({self.custom_year}) - {self.license_plate}"
    
    @property
    def kilometers_since_last_service(self):
        """Calculate kilometers since last service"""
        if self.last_service_odometer:
            return self.current_odometer - self.last_service_odometer
        return None
    
    @property
    def is_warranty_valid(self):
        """Check if warranty is still valid"""
        if not self.has_warranty or not self.warranty_end_date:
            return False
        return timezone.now().date() <= self.warranty_end_date
    
    @property
    def days_until_warranty_expires(self):
        """Days until warranty expires"""
        if not self.is_warranty_valid:
            return 0
        delta = self.warranty_end_date - timezone.now().date()
        return max(0, delta.days)
    
    @property
    def needs_10000km_service(self):
        """Check if vehicle needs 10,000 KM service"""
        if not self.is_eligible_for_10000km_service:
            return False
        
        if self.last_service_odometer and self.current_odometer:
            km_since_service = self.current_odometer - self.last_service_odometer
            if km_since_service >= 10000:
                return True
        
        if self.next_service_due_km and self.current_odometer >= self.next_service_due_km:
            return True
        
        if self.next_service_due_date and timezone.now().date() >= self.next_service_due_date:
            return True
        
        return False
    
    def update_service_info(self, service_type, odometer_after_service):
        """Update service information after service completion"""
        self.last_service_date = timezone.now().date()
        self.last_service_odometer = odometer_after_service
        self.last_service_type = service_type
        self.next_service_due_km = odometer_after_service + 10000
        self.next_service_due_date = timezone.now().date() + timezone.timedelta(days=365)  # 1 year
        self.save()


class ServiceBooking(models.Model):
    """Service booking model"""
    BOOKING_STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('confirmed', 'Confirmed'),
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
        ('no_show', 'No Show'),
    ]
    
    PRIORITY_CHOICES = [
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
        ('emergency', 'Emergency'),
        ('warranty', 'Warranty Claim'),
    ]
    
    SERVICE_TYPE_CHOICES = [
        ('neta_warranty', 'NETA 2-Year Warranty Service'),
        ('10000km_service', '10,000 KM Service'),
        ('routine_maintenance', 'Routine Maintenance'),
        ('battery_service', 'Battery Service'),
        ('diagnostic', 'Diagnostic Check'),
        ('repair', 'Repair Service'),
        ('recall_service', 'Recall Service'),
        ('pre_purchase_inspection', 'Pre-Purchase Inspection'),
        ('other', 'Other'),
    ]
    
    # Booking information
    booking_number = models.CharField(
        max_length=20,
        unique=True,
        default=generate_booking_number
    )
    # customer = models.ForeignKey(
    #     User,
    #     on_delete=models.CASCADE,
    #     related_name='service_bookings'
    # )
    customer = models.CharField(
        max_length=255,  # enough to store full name
        help_text="Full name of the customer",
    )

    vehicle = models.ForeignKey(
        ElectricCar,
        on_delete=models.CASCADE,
        related_name='service_bookings'
    )
    
    # Service details
    service_type = models.CharField(
        max_length=50,
        choices=SERVICE_TYPE_CHOICES,
        default='routine_maintenance'
    )
    service_type_custom = models.CharField(
        max_length=100,
        blank=True,
        help_text="Custom service type if 'other' is selected"
    )
    
    # Link to your existing Service model from company app
    service = models.ForeignKey(
        'company.Service',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings',
        help_text="Link to specific service from company app"
    )
    
    # Scheduling
    preferred_date = models.DateField()
    preferred_time_slot = models.TimeField()
    alternative_dates = models.JSONField(
        default=list,
        blank=True,
        help_text="List of alternative dates in YYYY-MM-DD format"
    )
    
    # Service details
    odometer_reading = models.IntegerField(
        help_text="Current odometer reading at time of booking"
    )
    service_description = models.TextField(
        blank=True,
        help_text="Detailed description of service needed"
    )
    symptoms_problems = models.TextField(
        blank=True,
        help_text="Describe any symptoms or problems"
    )
    
    # Priority and status
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='normal'
    )
    status = models.CharField(
        max_length=20,
        choices=BOOKING_STATUS_CHOICES,
        default='pending'
    )
    
    # Admin scheduling
    scheduled_date = models.DateField(null=True, blank=True)
    scheduled_time = models.TimeField(null=True, blank=True)
    scheduled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scheduled_bookings'
    )
    scheduled_at = models.DateTimeField(null=True, blank=True)
    
    # Completion
    assigned_technician = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_service_bookings',
        limit_choices_to={'groups__name': 'Technicians'}
    )
    service_center = models.ForeignKey(
        'company.ServiceCenter',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings'
    )
    
    # Completion details
    completed_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='completed_service_bookings'
    )
    final_odometer = models.IntegerField(null=True, blank=True)
    service_report = models.TextField(blank=True)
    parts_used = models.JSONField(
        default=list,
        blank=True,
        help_text="List of parts used with IDs and quantities"
    )
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    warranty_covered = models.BooleanField(default=False)
    warranty_claim_number = models.CharField(max_length=50, blank=True)
    
    # Customer communication
    customer_notes = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)
    
    # Notification flags
    confirmation_sent = models.BooleanField(default=False)
    reminder_sent = models.BooleanField(default=False)
    follow_up_sent = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Service Booking"
        verbose_name_plural = "Service Bookings"
        indexes = [
            models.Index(fields=['booking_number']),
            models.Index(fields=['status']),
            models.Index(fields=['scheduled_date']),
            models.Index(fields=['customer']),
        ]
    
    def __str__(self):
        return f"{self.booking_number} - {self.customer.username} - {self.vehicle.license_plate}"
    
    def save(self, *args, **kwargs):
        # Generate booking number if not set
        if not self.booking_number:
            self.booking_number = generate_booking_number()
        
        # Auto-update vehicle's current odometer
        if self.odometer_reading and self.vehicle.current_odometer != self.odometer_reading:
            self.vehicle.current_odometer = self.odometer_reading
            self.vehicle.save()
        
        # Check eligibility for specific services
        if self.service_type == 'neta_warranty':
            self._check_neta_warranty_eligibility()
        elif self.service_type == '10000km_service':
            self._check_10000km_eligibility()
        
        super().save(*args, **kwargs)
    
    def _check_neta_warranty_eligibility(self):
        """Check if vehicle is eligible for NETA warranty service"""
        self.warranty_covered = (
            self.vehicle.is_neta_car and 
            self.vehicle.is_warranty_valid and
            self.vehicle.days_until_warranty_expires > 0
        )
        if self.warranty_covered:
            self.priority = 'warranty'
    
    def _check_10000km_eligibility(self):
        """Check if vehicle is eligible for 10,000 KM service"""
        if self.vehicle.is_eligible_for_10000km_service:
            # Check if it's actually due for service
            if self.vehicle.needs_10000km_service:
                self.priority = 'normal'
            else:
                self.priority = 'normal'
                self.internal_notes += "\nNote: Vehicle may not be due for 10,000 KM service yet."
    
    @property
    def is_neta_warranty_booking(self):
        """Check if this is a NETA warranty booking"""
        return self.service_type == 'neta_warranty'
    
    @property
    def is_10000km_service_booking(self):
        """Check if this is a 10,000 KM service booking"""
        return self.service_type == '10000km_service'
    
    @property
    def can_be_scheduled(self):
        """Check if booking can be scheduled"""
        return self.status in ['pending', 'confirmed', 'rescheduled']
    
    @property
    def is_scheduled(self):
        """Check if booking is scheduled"""
        return self.scheduled_date is not None and self.scheduled_time is not None
    
    @property
    def scheduled_datetime(self):
        """Get scheduled datetime"""
        if self.scheduled_date and self.scheduled_time:
            return timezone.datetime.combine(self.scheduled_date, self.scheduled_time)
        return None
    
    @property
    def days_until_scheduled(self):
        """Days until scheduled service"""
        if self.scheduled_date:
            delta = self.scheduled_date - timezone.now().date()
            return delta.days
        return None
    
    def schedule_service(self, date, time, scheduled_by, service_center=None):
        """Schedule the service"""
        if not self.can_be_scheduled:
            raise ValueError("Booking cannot be scheduled in its current status")
        
        self.scheduled_date = date
        self.scheduled_time = time
        self.scheduled_by = scheduled_by
        self.scheduled_at = timezone.now()
        self.status = 'scheduled'
        
        if service_center:
            self.service_center = service_center
        
        self.save()
        
        # Send confirmation email
        self.send_schedule_confirmation()
    
    def send_schedule_confirmation(self):
        """Send schedule confirmation email to customer"""
        if not self.scheduled_datetime:
            return
        
        subject = f"Service Scheduled - Booking #{self.booking_number}"
        
        # Prepare email context
        context = {
            'booking': self,
            'customer': self.customer,
            'vehicle': self.vehicle,
            'scheduled_datetime': self.scheduled_datetime,
            'service_center': self.service_center,
        }
        
        html_message = render_to_string('emails/service_scheduled.html', context)
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.customer.email],
                fail_silently=False,
            )
            self.confirmation_sent = True
            self.save()
            return True
        except Exception as e:
            # Log error
            print(f"Failed to send email: {e}")
            return False
    
    def complete_service(self, technician, final_odometer, report, parts_used=None, total_cost=None):
        """Mark service as completed"""
        if self.status not in ['scheduled', 'in_progress']:
            raise ValueError("Cannot complete service in current status")
        
        self.assigned_technician = technician
        self.final_odometer = final_odometer
        self.service_report = report
        self.completed_at = timezone.now()
        self.completed_by = technician
        self.status = 'completed'
        
        if parts_used:
            self.parts_used = parts_used
        
        if total_cost is not None:
            self.total_cost = total_cost
        
        # Update vehicle service information
        service_type = self.service_type_custom if self.service_type == 'other' else self.get_service_type_display()
        self.vehicle.update_service_info(service_type, final_odometer)
        
        self.save()
        
        # Send completion email
        self.send_completion_confirmation()
    
    def send_completion_confirmation(self):
        """Send service completion email"""
        subject = f"Service Completed - Booking #{self.booking_number}"
        
        context = {
            'booking': self,
            'customer': self.customer,
            'vehicle': self.vehicle,
            'completed_at': self.completed_at,
        }
        
        html_message = render_to_string('emails/service_completed.html', context)
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.customer.email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Failed to send completion email: {e}")
            return False

    def get_customer_full_name(self):
        """Get customer's full name"""
        if self.customer.first_name and self.customer.last_name:
            return f"{self.customer.first_name} {self.customer.last_name}"
        return self.customer.username
    
    def get_customer_email(self):
        """Get customer's email"""
        return self.customer.email
    
    def send_schedule_confirmation(self):
        """Send schedule confirmation email to customer"""
        if not self.scheduled_datetime:
            return False
        
        subject = f"Service Appointment Confirmed - Booking #{self.booking_number}"
        
        # Prepare email context
        context = {
            'booking': self,
            'customer_name': self.get_customer_full_name(),
            'customer_email': self.get_customer_email(),
            'vehicle': self.vehicle,
            'scheduled_date': self.scheduled_date.strftime('%B %d, %Y'),
            'scheduled_time': self.scheduled_time.strftime('%I:%M %p'),
            'service_type': self.get_service_type_display(),
            'service_center': self.service_center,
            'booking_number': self.booking_number,
        }
        
        try:
            # Render HTML email
            html_content = render_to_string('emails/service_scheduled.html', context)
            text_content = strip_tags(html_content)
            
            # Create email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[self.get_customer_email()],
                reply_to=[settings.SERVICE_EMAIL or settings.DEFAULT_FROM_EMAIL]
            )
            email.attach_alternative(html_content, "text/html")
            
            # Send email
            email.send(fail_silently=False)
            
            self.confirmation_sent = True
            self.save(update_fields=['confirmation_sent'])
            return True
            
        except Exception as e:
            # Log error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send schedule confirmation email: {e}")
            return False
    
    def send_booking_received_email(self):
        """Send booking received confirmation email"""
        subject = f"Service Booking Received - Booking #{self.booking_number}"
        
        context = {
            'booking': self,
            'customer_name': self.get_customer_full_name(),
            'customer_email': self.get_customer_email(),
            'vehicle': self.vehicle,
            'preferred_date': self.preferred_date.strftime('%B %d, %Y'),
            'service_type': self.get_service_type_display(),
            'booking_number': self.booking_number,
            'estimated_response_time': '24 hours',
            'service_phone': '+251 11 123 4567',
            'service_email': 'service@etopikar.com',
        }
        
        try:
            html_content = render_to_string('emails/booking_received.html', context)
            text_content = strip_tags(html_content)
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[self.get_customer_email()],
                reply_to=[settings.SERVICE_EMAIL or settings.DEFAULT_FROM_EMAIL]
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)
            return True
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send booking received email: {e}")
            return False
    
    def send_service_completion_email(self):
        """Send service completion email"""
        subject = f"Service Completed - Booking #{self.booking_number}"
        
        context = {
            'booking': self,
            'customer_name': self.get_customer_full_name(),
            'customer_email': self.get_customer_email(),
            'vehicle': self.vehicle,
            'completed_date': self.completed_at.strftime('%B %d, %Y') if self.completed_at else '',
            'service_report': self.service_report,
            'total_cost': self.total_cost,
            'warranty_covered': self.warranty_covered,
            'booking_number': self.booking_number,
        }
        
        try:
            html_content = render_to_string('emails/service_completed.html', context)
            text_content = strip_tags(html_content)
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[self.get_customer_email()],
                reply_to=[settings.SERVICE_EMAIL or settings.DEFAULT_FROM_EMAIL]
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)
            return True
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send service completion email: {e}")
            return False
    
    def save(self, *args, **kwargs):
        # Send booking received email when status changes to pending
        is_new = self._state.adding
        old_status = None
        if not is_new:
            old_instance = ServiceBooking.objects.filter(pk=self.pk).first()
            if old_instance:
                old_status = old_instance.status
        
        super().save(*args, **kwargs)
        
        # Send booking received email for new bookings
        if is_new and self.status == 'pending':
            self.send_booking_received_email()
        
        # Send schedule confirmation when scheduled
        if not is_new and old_status != 'scheduled' and self.status == 'scheduled':
            self.send_schedule_confirmation()
        
        # Send completion email when completed
        if not is_new and old_status != 'completed' and self.status == 'completed':
            self.send_service_completion_email()

class ServiceReminder(models.Model):
    """Service reminders for customers"""
    REMINDER_TYPE_CHOICES = [
        ('upcoming_service', 'Upcoming Service'),
        ('warranty_expiry', 'Warranty Expiry'),
        ('regular_maintenance', 'Regular Maintenance'),
        ('recall_notice', 'Recall Notice'),
        ('promotional', 'Promotional Service'),
    ]
    
    vehicle = models.ForeignKey(
        CustomerVehicle,
        on_delete=models.CASCADE,
        related_name='reminders'
    )
    reminder_type = models.CharField(
        max_length=50,
        choices=REMINDER_TYPE_CHOICES
    )
    reminder_date = models.DateField()
    message = models.TextField()
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    scheduled_send_date = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scheduled_send_date']
    
    def __str__(self):
        return f"{self.vehicle.license_plate} - {self.get_reminder_type_display()}"