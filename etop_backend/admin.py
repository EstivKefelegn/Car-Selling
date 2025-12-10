from django.contrib import admin
from .models import Manufacturer, ElectricCar, EVReview, ChargingSpecification, EVComparison, CarColor
from django.utils.html import format_html


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'is_ev_only', 'founded_year']
    list_filter = ['country', 'is_ev_only']
    search_fields = ['name', 'country']


class ChargingSpecificationInline(admin.TabularInline):
    model = ChargingSpecification
    extra = 0


@admin.register(ElectricCar)
class ElectricCarAdmin(admin.ModelAdmin):
    list_display = [
        'model_name',
        'manufacturer',
        'variant',
        'model_year',
        'battery_capacity',
        'range_epa',
        'exterior_color_preview',   # 👈 Add preview here
    ]

    list_filter = ['manufacturer', 'model_year', 'drive_type', 'production_status']
    search_fields = ['model_name', 'manufacturer__name', 'variant']
    inlines = [ChargingSpecificationInline]

    filter_horizontal = ('exterior_colors', 'interior_colors')

    fieldsets = (
        ('Basic Information', {
            'fields': ('manufacturer', 'model_name', 'variant', 'model_year', 'production_status')
        }),
        ('Colors', {
            'fields': ('exterior_colors', 'interior_colors')
        }),
        ('Battery & Performance', {
            'fields': ('battery_capacity', 'battery_type', 'range_epa', 'range_wltp',
                      'acceleration_0_60', 'top_speed', 'motor_power', 'drive_type')
        }),
        ('Charging', {
            'fields': ('fast_charging_support', 'max_dc_charging_power', 'charging_type',
                      'charging_time_10_80')
        }),
        ('Features', {
            'fields': ('has_heat_pump', 'has_battery_preconditioning', 'has_v2l',
                      'has_one_pedal_driving')
        }),
        ('Pricing & Availability', {
            'fields': ('base_price', 'eligible_for_tax_credit', 'is_available', 'release_date')
        }),
        ('Media', {
            'fields': ('main_image',)
        }),
    )

    # 👇 Add the preview method INSIDE the admin class
    def exterior_color_preview(self, obj):
        colors = obj.exterior_colors.all()
        return format_html(''.join(
            f'<div style="width: 18px; height: 18px; background:{c.hex_code}; '
            f'display:inline-block; margin-right:3px; border:1px solid #333"></div>'
            for c in colors if c.hex_code
        ))

    exterior_color_preview.short_description = "Exterior Colors"   # Name shown in admin list


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

@admin.register(CarColor)
class CarColorAdmin(admin.ModelAdmin):
    list_display = ("name", "color_type", "hex_code", "color_preview")
    list_filter = ("color_type",)
    search_fields = ("name",)
    ordering = ("color_type", "name")

    def color_preview(self, obj):
        if obj.hex_code:
            return format_html(
                '<div style="width: 20px; height: 20px; background:{}; '
                'border:1px solid #333; display:inline-block;"></div>',
                obj.hex_code
            )
        return "-"
    
    color_preview.short_description = "Preview"