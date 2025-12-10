from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Manufacturer, CarColor, ElectricCar, CarColorImage, CarColorConfiguration, EVReview, EVComparison)


# ========== INLINES ==========
class CarColorImageInline(admin.TabularInline):
    """Inline for car color images"""
    model = CarColorImage
    extra = 1
    fields = ['exterior_color', 'interior_color', 'image_type', 'image_preview', 'image', 'description', 'is_primary', 'order']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 150px; border-radius: 5px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Preview'


class CarColorConfigurationInline(admin.TabularInline):
    """Inline for color configurations"""
    model = CarColorConfiguration
    extra = 1
    fields = ['exterior_color', 'interior_color', 'price_adjustment', 'total_price', 'is_popular', 'is_available', 'delivery_time']
    readonly_fields = ['total_price']
    
    def total_price(self, obj):
        return f"ETB {obj.total_price:,.2f}"
    total_price.short_description = 'Total Price'



# ========== MANUFACTURER ADMIN ==========
@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'founded_year', 'is_ev_only', 'logo_preview', 'car_count']
    list_filter = ['country', 'is_ev_only', 'founded_year']
    search_fields = ['name', 'country', 'headquarters']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'country', 'founded_year', 'is_ev_only', 'headquarters')
        }),
        ('Details', {
            'fields': ('description', 'website', 'logo')
        }),
    )
    readonly_fields = ['car_count']
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.logo.url)
        return "No logo"
    logo_preview.short_description = 'Logo'
    
    def car_count(self, obj):
        count = obj.electric_cars.count()
        # url = reverse('admin:app_electriccar_changelist') + f'?manufacturer__id__exact={obj.id}'
        url = reverse('admin:etop_backend_electriccar_changelist') + f'?manufacturer__id__exact={obj.id}'
        # return format_html('<a href="{}">{} cars</a>', url, count)
        return format_html('<a href="{}">{} cars</a>', url, count)
    car_count.short_description = 'Cars'


# ========== CAR COLOR ADMIN ==========
@admin.register(CarColor)
class CarColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_type', 'hex_code', 'color_preview', 'image_preview']
    list_filter = ['color_type']
    search_fields = ['name', 'hex_code']
    fields = ['name', 'color_type', 'hex_code', 'color_preview_field', 'image', 'description']
    readonly_fields = ['color_preview_field']
    
    def color_preview(self, obj):
        if obj.hex_code:
            return format_html(
                '<div style="background-color: {}; width: 30px; height: 30px; border-radius: 50%; border: 1px solid #ddd;"></div>',
                obj.hex_code
            )
        return "No color code"
    color_preview.short_description = 'Color'
    
    def color_preview_field(self, obj):
        if obj.hex_code:
            return format_html(
                '<div style="background-color: {}; width: 100px; height: 100px; border-radius: 10px; border: 2px solid #ddd; margin: 10px 0;"></div>',
                obj.hex_code
            )
        return "No color code"
    color_preview_field.short_description = 'Color Preview'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Image'


# ========== ELECTRIC CAR ADMIN ==========
@admin.register(ElectricCar)
class ElectricCarAdmin(admin.ModelAdmin):
    list_display = [
        'model_name', 'manufacturer_link', 'model_year', 'category', 
        'base_price_display', 'status_badge', 'featured', 'main_image_preview'
    ]
    list_filter = ['manufacturer', 'model_year', 'category', 'status', 'featured', 'battery_type']
    search_fields = ['model_name', 'variant', 'manufacturer__name']
    list_editable = ['featured']
    filter_horizontal = ['available_exterior_colors', 'available_interior_colors']
    inlines = [CarColorConfigurationInline, CarColorImageInline]
    readonly_fields = ['slug', 'created_at', 'updated_at', 'efficiency_display', 'charging_speed_display']
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'manufacturer', 'model_name', 'variant', 'model_year', 'category', 
                'status', 'featured', 'slug', 'main_image', 'description'
            )
        }),
        ('Battery & Performance', {
            'fields': (
                'battery_capacity', 'usable_battery', 'battery_type', 
                'battery_warranty_years', 'battery_warranty_km',
                'range_wltp', 'range_epa', 'energy_consumption',
                'acceleration_0_100', 'top_speed', 'motor_power', 'torque', 'drive_type'
            )
        }),
        ('Charging', {
            'fields': (
                'max_dc_charging', 'max_ac_charging', 'charging_type',
                'charging_time_10_80', 'charging_time_0_100_ac'
            )
        }),
        ('Dimensions & Capacity', {
            'fields': (
                'length', 'width', 'height', 'wheelbase',
                'curb_weight', 'cargo_capacity', 'seating_capacity'
            )
        }),
        ('Color Options', {
            'fields': ('available_exterior_colors', 'available_interior_colors')
        }),
        ('Features & Technology', {
            'fields': (
                'has_heat_pump', 'has_battery_preconditioning',
                'has_v2l', 'has_v2g', 'has_one_pedal_driving',
                'regen_braking_levels', 'autopilot_level', 'charging_port_location'
            )
        }),
        ('Pricing & Availability', {
            'fields': (
                'base_price', 'estimated_delivery', 'tax_incentive',
                'key_features', 'safety_features', 'brochure'
            )
        }),
        ('Calculated Fields', {
            'fields': ('efficiency_display', 'charging_speed_display'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def manufacturer_link(self, obj):
        url = reverse('admin:etop_backend_manufacturer_change', args=[obj.manufacturer.id])
        return format_html('<a href="{}">{}</a>', url, obj.manufacturer.name)
    manufacturer_link.short_description = 'Manufacturer'

    
    def base_price_display(self, obj):
        return f"ETB {obj.base_price:,.2f}"
    base_price_display.short_description = 'Price'
    
    def status_badge(self, obj):
        colors = {
            'available': 'green',
            'reserved': 'orange',
            'sold': 'red',
            'coming_soon': 'blue',
            'pre_order': 'purple',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def main_image_preview(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" style="max-height: 50px; border-radius: 5px;" />', obj.main_image.url)
        return "No image"
    main_image_preview.short_description = 'Image'
    
    def efficiency_display(self, obj):
        eff = obj.efficiency
        if eff:
            return f"{eff} km/kWh"
        return "N/A"
    efficiency_display.short_description = 'Efficiency'
    
    def charging_speed_display(self, obj):
        speed = obj.charging_speed
        if speed:
            return f"{speed} km/min"
        return "N/A"
    charging_speed_display.short_description = 'Charging Speed'


# ========== CAR COLOR CONFIGURATION ADMIN ==========
@admin.register(CarColorConfiguration)
class CarColorConfigurationAdmin(admin.ModelAdmin):
    list_display = ['car_link', 'exterior_color', 'interior_color', 'price_adjustment_display', 'total_price_display', 'is_popular', 'is_available']
    list_filter = ['car', 'is_popular', 'is_available']
    search_fields = ['car__model_name', 'exterior_color__name', 'interior_color__name']
    list_editable = ['is_popular', 'is_available']
    readonly_fields = ['total_price_display_field', 'primary_image_preview']
    
    def car_link(self, obj):
        url = reverse('admin:etop_backend_electriccar_change', args=[obj.car.id])
        return format_html('<a href="{}">{}</a>', url, obj.car.display_name)
    car_link.short_description = 'Car'

    
    def price_adjustment_display(self, obj):
        if obj.price_adjustment > 0:
            return format_html('<span style="color: green;">+ETB {:,}</span>', obj.price_adjustment)
        elif obj.price_adjustment < 0:
            return format_html('<span style="color: red;">-ETB {:,}</span>', abs(obj.price_adjustment))
        return "ETB 0"
    price_adjustment_display.short_description = 'Price Adjustment'
    
    def total_price_display(self, obj):
        return f"ETB {obj.total_price:,.2f}"
    total_price_display.short_description = 'Total Price'
    
    def total_price_display_field(self, obj):
        return f"ETB {obj.total_price:,.2f}"
    total_price_display_field.short_description = 'Total Price'
    
    def primary_image_preview(self, obj):
        img = obj.primary_image
        if img and img.image:
            return format_html('<img src="{}" style="max-height: 200px; max-width: 300px;" />', img.image.url)
        return "No primary image"
    primary_image_preview.short_description = 'Primary Image'




@admin.register(EVReview)
class EVReviewAdmin(admin.ModelAdmin):
    list_display = ['car', 'reviewer_name', 'rating', 'verified_owner', 'review_date']
    list_filter = ['rating', 'verified_owner', 'review_date']
    search_fields = ['reviewer_name', 'car__model_name', 'review_text']


@admin.register(EVComparison)
class EVComparisonAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    filter_horizontal = ['cars']
    search_fields = ['name', 'description']

# ========== ADMIN SITE CUSTOMIZATION ==========
from django.contrib.admin import AdminSite

class CarSalesAdminSite(AdminSite):
    site_header = "Etiopikar Electric Cars Administration"
    site_title = "Etiopikar EV Admin"
    index_title = "Welcome to Etiopikar Electric Car Sales Admin"


# Or register with default admin site
admin.site.site_header = "Etiopikar Electric Cars Administration"
admin.site.site_title = "Etiopikar EV Admin"
admin.site.index_title = "Welcome to Etiopikar Electric Car Sales Admin"
