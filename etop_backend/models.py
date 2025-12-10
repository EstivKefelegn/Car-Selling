from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Manufacturer(models.Model):
    """Electric vehicle manufacturer"""
    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=100)
    founded_year = models.IntegerField(null=True, blank=True)
    is_ev_only = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return self.name

class CarColor(models.Model):
    COLOR_TYPE_CHOICES = [
        ("exterior", "Exterior Color"),
        ("interior", "Interior Color"),
    ]

    name = models.CharField(max_length=50)
    hex_code = models.CharField(max_length=7, blank=True, null=True)  # Optional, like #FFFFFF
    color_type = models.CharField(max_length=20, choices=COLOR_TYPE_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.color_type})"



class ElectricCar(models.Model):
    """Model for electric vehicles"""
    
    CHARGING_TYPE_CHOICES = [
        ('type1', 'Type 1 (SAE J1772)'),
        ('type2', 'Type 2 (Mennekes)'),
        ('ccs1', 'CCS1 (Combo 1)'),
        ('ccs2', 'CCS2 (Combo 2)'),
        ('chademo', 'CHAdeMO'),
        ('tesla', 'Tesla Supercharger'),
        ('gb_t', 'GB/T (China)'),
    ]
    
    BATTERY_TYPE_CHOICES = [
        ('lithium_ion', 'Lithium-Ion'),
        ('lithium_polymer', 'Lithium Polymer'),
        ('solid_state', 'Solid State'),
        ('lifepo4', 'Lithium Iron Phosphate (LiFePO4)'),
    ]
    
    DRIVE_TYPE_CHOICES = [
        ('rwd', 'Rear Wheel Drive'),
        ('fwd', 'Front Wheel Drive'),
        ('awd', 'All Wheel Drive'),
        ('dual_motor', 'Dual Motor AWD'),
        ('tri_motor', 'Tri Motor AWD'),
    ]
    
    # Basic Information
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, related_name='electric_cars')
    model_name = models.CharField(max_length=100)
    variant = models.CharField(max_length=100, blank=True)  # e.g., "Long Range", "Performance"
    model_year = models.IntegerField(
        validators=[MinValueValidator(2008), MaxValueValidator(2025)]
    )
    
    # Battery Information
    battery_capacity = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        help_text="Battery capacity in kWh"
    )
    battery_type = models.CharField(max_length=20, choices=BATTERY_TYPE_CHOICES, default='lithium_ion')
    usable_battery = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Usable battery capacity in kWh"
    )
    
    # Performance
    range_epa = models.IntegerField(
        help_text="EPA estimated range in miles",
        null=True,
        blank=True
    )
    range_wltp = models.IntegerField(
        help_text="WLTP estimated range in miles",
        null=True,
        blank=True
    )
    acceleration_0_60 = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        help_text="0-60 mph acceleration in seconds",
        null=True,
        blank=True
    )
    top_speed = models.IntegerField(
        help_text="Top speed in mph",
        null=True,
        blank=True
    )
    
    # Charging
    fast_charging_support = models.BooleanField(default=True)
    max_dc_charging_power = models.IntegerField(
        help_text="Maximum DC charging power in kW",
        null=True,
        blank=True
    )
    max_ac_charging_power = models.IntegerField(
        help_text="Maximum AC charging power in kW",
        null=True,
        blank=True
    )
    charging_type = models.CharField(
        max_length=20,
        choices=CHARGING_TYPE_CHOICES,
        default='ccs1'
    )
    charging_time_10_80 = models.IntegerField(
        help_text="Time to charge from 10% to 80% at max DC power (minutes)",
        null=True,
        blank=True
    )
    
    # Powertrain
    motor_power = models.IntegerField(help_text="Motor power in kW")
    torque = models.IntegerField(help_text="Torque in Nm", null=True, blank=True)
    drive_type = models.CharField(max_length=20, choices=DRIVE_TYPE_CHOICES)
    
    # Dimensions & Weight
    length = models.DecimalField(max_digits=5, decimal_places=1, help_text="Length in mm", null=True, blank=True)
    width = models.DecimalField(max_digits=5, decimal_places=1, help_text="Width in mm", null=True, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=1, help_text="Height in mm", null=True, blank=True)
    curb_weight = models.IntegerField(help_text="Curb weight in kg", null=True, blank=True)
    frunk_capacity = models.DecimalField(
        max_digits=4, 
        decimal_places=1,
        help_text="Front trunk capacity in liters",
        null=True,
        blank=True
    )
    trunk_capacity = models.DecimalField(
        max_digits=4, 
        decimal_places=1,
        help_text="Rear trunk capacity in liters",
        null=True,
        blank=True
    )
    
    # Features
    has_heat_pump = models.BooleanField(default=False)
    has_battery_preconditioning = models.BooleanField(default=False)
    has_v2l = models.BooleanField(
        default=False,
        help_text="Vehicle-to-Load capability"
    )
    has_v2g = models.BooleanField(
        default=False,
        help_text="Vehicle-to-Grid capability"
    )
    has_one_pedal_driving = models.BooleanField(default=False)
    regen_braking_levels = models.IntegerField(
        default=1,
        help_text="Number of regenerative braking levels"
    )
    
    # Pricing
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Base price in USD",
        null=True,
        blank=True
    )
    eligible_for_tax_credit = models.BooleanField(default=False)
    
    # Additional Info
    release_date = models.DateField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    production_status = models.CharField(
        max_length=20,
        choices=[
            ('concept', 'Concept'),
            ('pre_order', 'Pre-order'),
            ('production', 'In Production'),
            ('discontinued', 'Discontinued'),
        ],
        default='production'
    )
    
    # Images
    main_image = models.ImageField(upload_to='ev_images/', null=True, blank=True)
    
    exterior_colors = models.ManyToManyField(
        CarColor,
        related_name="exterior_cars",
        limit_choices_to={"color_type": "exterior"},
        blank=True
    )

    interior_colors = models.ManyToManyField(
        CarColor,
        related_name="interior_cars",
        limit_choices_to={"color_type": "interior"},
        blank=True
    )


    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['manufacturer', 'model_name', 'model_year']
        unique_together = ['manufacturer', 'model_name', 'variant', 'model_year']
        verbose_name = "Electric Car"
        verbose_name_plural = "Electric Cars"
    
    def __str__(self):
        return f"{self.manufacturer.name} {self.model_name} {self.variant} ({self.model_year})"
    
    @property
    def full_model_name(self):
        if self.variant:
            return f"{self.manufacturer.name} {self.model_name} {self.variant}"
        return f"{self.manufacturer.name} {self.model_name}"
    
    @property
    def battery_efficiency(self):
        """Calculate efficiency in miles per kWh"""
        if self.range_epa and self.battery_capacity:
            return round(self.range_epa / float(self.battery_capacity), 2)
        return None
    
    @property
    def charging_speed(self):
        """Calculate charging speed in miles per minute"""
        if self.max_dc_charging_power and self.battery_efficiency:
            return round((self.max_dc_charging_power * self.battery_efficiency) / 60, 2)
        return None


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