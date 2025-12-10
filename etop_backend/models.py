# models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from decimal import Decimal


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