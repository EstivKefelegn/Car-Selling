from django.contrib import admin, messages
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.html import format_html

from .models import (
    Manufacturer, CarColor, ElectricCar, CarColorImage, 
    CarColorConfiguration, EVReview, EVComparison, 
    EmailSubscriber, CustomerVehicle, ServiceBooking, ServiceReminder, ContactOrder, ScheduleService)
from django.contrib.auth.admin import UserAdmin


from django.urls import reverse
from django.utils import timezone


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


# Register your models here.
@admin.register(EmailSubscriber)
class EmailSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'sales_associate', 'subscription_status', 
                   'receive_inventory_alerts', 'subscribed_at')
    list_filter = ('subscription_status', 'receive_inventory_alerts', 
                  'sales_associate', 'subscribed_at')
    search_fields = ('email', 'first_name', 'last_name')
    readonly_fields = ('subscribed_at', 'updated_at', 'unsubscribed_at')
    fieldsets = (
        ('Subscriber Information', {
            'fields': ('email', 'first_name', 'last_name')
        }),
        ('Sales Associate Information', {
            'fields': ('sales_associate',),
            'description': 'Select a staff member if they referred this subscriber'
        }),
        ('Subscription Settings', {
            'fields': ('subscription_status', 'receive_inventory_alerts')
        }),
        ('Timestamps', {
            'fields': ('subscribed_at', 'updated_at', 'unsubscribed_at'),
            'classes': ('collapse',)
        }),
        ('Admin Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_unsubscribed', 'mark_as_active', 'enable_inventory_alerts', 
               'disable_inventory_alerts']
    
    def mark_as_unsubscribed(self, request, queryset):
        queryset.update(subscription_status=EmailSubscriber.SubscriptionStatus.UNSUBSCRIBED)
        self.message_user(request, f"{queryset.count()} subscribers marked as unsubscribed")
    mark_as_unsubscribed.short_description = "Mark selected as unsubscribed"
    
    def mark_as_active(self, request, queryset):
        queryset.update(subscription_status=EmailSubscriber.SubscriptionStatus.ACTIVE)
        self.message_user(request, f"{queryset.count()} subscribers marked as active")
    mark_as_active.short_description = "Mark selected as active"
    
    def enable_inventory_alerts(self, request, queryset):
        queryset.update(receive_inventory_alerts=True)
        self.message_user(request, f"Enabled inventory alerts for {queryset.count()} subscribers")
    enable_inventory_alerts.short_description = "Enable inventory alerts"
    
    def disable_inventory_alerts(self, request, queryset):
        queryset.update(receive_inventory_alerts=False)
        self.message_user(request, f"Disabled inventory alerts for {queryset.count()} subscribers")
    disable_inventory_alerts.short_description = "Disable inventory alerts"
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Customize the sales associate queryset to only show staff users
        if 'sales_associate' in form.base_fields:
            form.base_fields['sales_associate'].queryset = User.objects.filter(is_staff=True)
        return form



@admin.register(CustomerVehicle)
class CustomerVehicleAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'customer', 'license_plate', 'vin', 'is_neta_car', 
                   'current_odometer', 'needs_10000km_service', 'is_warranty_valid')
    list_filter = ('is_neta_car', 'source', 'has_warranty', 'is_eligible_for_10000km_service')
    search_fields = ('license_plate', 'vin', 'customer__username', 'customer__email',
                    'custom_make', 'custom_model')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Owner Information', {
            'fields': ('customer',)
        }),
        ('Vehicle Information', {
            'fields': ('electric_car', 'custom_make', 'custom_model', 'custom_year',
                      'license_plate', 'vin', 'color')
        }),
        ('Purchase Information', {
            'fields': ('source', 'purchased_from_us', 'purchase_date',
                      'purchase_odometer', 'sales_invoice_number')
        }),
        ('Service History', {
            'fields': ('current_odometer', 'last_service_date', 'last_service_odometer',
                      'last_service_type')
        }),
        ('Warranty Information', {
            'fields': ('has_warranty', 'warranty_start_date', 'warranty_end_date',
                      'warranty_type', 'warranty_terms')
        }),
        ('NETA Specific', {
            'fields': ('is_neta_car', 'neta_battery_warranty_years',
                      'neta_battery_warranty_km')
        }),
        ('10,000 KM Service', {
            'fields': ('is_eligible_for_10000km_service', 'next_service_due_km',
                      'next_service_due_date')
        }),
        ('Additional Information', {
            'fields': ('additional_notes', 'created_at', 'updated_at')
        }),
    )
    
    def view_bookings(self, obj):
        url = reverse('admin:app_servicebooking_changelist') + f'?vehicle__id__exact={obj.id}'
        return format_html('<a href="{}">View Bookings</a>', url)
    view_bookings.short_description = "Service Bookings"


@admin.register(ServiceBooking)
class ServiceBookingAdmin(admin.ModelAdmin):
    list_display = [
        'booking_number',
        'customer',
        'vehicle',
        'service_type',
        'preferred_date',
        'status',
        'priority',
        'is_scheduled_display',  # Custom column
        'created_at'
    ]
    
    list_filter = [
        'status',
        'service_type',
        'is_scheduled',
        'priority',
        'created_at'
    ]
    
    search_fields = [
        'booking_number',
        'customer',
        'customer_email',
        'vehicle__license_plate',
        'vehicle__vin'
    ]
    
    readonly_fields = [
        'booking_number',
        'created_at',
        'updated_at',
        'get_customer_full_name',
        'get_customer_email',
    ]
    
    fieldsets = (
        ('Booking Information', {
            'fields': (
                'booking_number',
                'customer',
                'customer_email',
                'customer_phone',
                'vehicle',
                'preferred_date',
                'preferred_time_slot',
                'alternative_dates',
            )
        }),
        ('Service Details', {
            'fields': (
                'service_type',
                'service_type_custom',
                'odometer_reading',
                'service_description',
                'symptoms_problems',
                'customer_notes',
            )
        }),
        ('Scheduling', {
            'fields': (
                'is_scheduled',
                'status',
                'priority',
                'service_center',
            )
        }),
        ('Completion', {
            'fields': (
                'assigned_technician',
                'completed_at',
                'completed_by',
                'final_odometer',
                'service_report',
                'parts_used',
                'total_cost',
                'warranty_covered',
                'warranty_claim_number',
            )
        }),
        ('System Information', {
            'fields': (
                'created_at',
                'updated_at',
                'confirmation_sent',
                'reminder_sent',
                'follow_up_sent',
            )
        }),
    )
    
    # Custom display for is_scheduled
    def is_scheduled_display(self, obj):
        if obj.is_scheduled:
            return format_html('<span style="color: green;">✓ Scheduled</span>')
        else:
            return format_html('<span style="color: red; font-weight: bold;">⚠️ Needs Scheduling</span>')
    is_scheduled_display.short_description = 'Scheduled Status'
    
    # Custom action to mark as scheduled
    actions = ['mark_as_scheduled', 'mark_as_completed']
    
    def mark_as_scheduled(self, request, queryset):
        updated = queryset.update(is_scheduled=True, status='scheduled')
        self.message_user(request, f"Marked {updated} booking(s) as scheduled.")
    mark_as_scheduled.short_description = "Mark selected bookings as scheduled"
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(
            status='completed',
            completed_at=timezone.now(),
            completed_by=request.user
        )
        self.message_user(request, f"Marked {updated} booking(s) as completed.")
    mark_as_completed.short_description = "Mark selected bookings as completed"
    
    # Show alerts on admin changelist
    def changelist_view(self, request, extra_context=None):
        # Count unscheduled services
        unscheduled_count = ServiceBooking.objects.filter(
            is_scheduled=False,
            status__in=['pending', 'confirmed']
        ).count()
        
        urgent_unscheduled_count = ServiceBooking.objects.filter(
            is_scheduled=False,
            status='pending',
            priority__in=['urgent', 'emergency']
        ).count()
        
        overdue_count = ServiceBooking.objects.filter(
            preferred_date__lt=timezone.now().date(),
            status__in=['pending', 'confirmed']
        ).count()
        
        # Add alerts
        if urgent_unscheduled_count > 0:
            messages.error(
                request,
                f"🚨 URGENT ALERT: {urgent_unscheduled_count} urgent booking(s) need immediate scheduling!"
            )
        
        if unscheduled_count > 0:
            messages.warning(
                request,
                f"🔧 {unscheduled_count} booking(s) are waiting to be scheduled!"
            )
        
        if overdue_count > 0:
            messages.error(
                request,
                f"⏰ {overdue_count} booking(s) have preferred dates that have passed!"
            )
        
        return super().changelist_view(request, extra_context)
    
    # Custom methods for readonly fields
    def get_customer_full_name(self, obj):
        return obj.customer
    get_customer_full_name.short_description = 'Customer Name'
    
    def get_customer_email(self, obj):
        return obj.customer_email
    get_customer_email.short_description = 'Customer Email'

@admin.register(ScheduleService)
class ScheduleServiceAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'scheduled_date',
        'scheduled_time',
        'service_center',
        'scheduled_by',
        'created_at'
    ]
    
    list_filter = [
        'scheduled_date',
        'service_center',
    ]
    
    filter_horizontal = ['bookings']  # For easier selection of bookings
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only for new objects
            obj.scheduled_by = request.user
        super().save_model(request, obj, form, change)
        
        # Apply schedule if this is a new ScheduleService
        if not change:
            obj.apply_schedule()

# @admin.register(ScheduleService)
# class ScheduleServiceAdmin(admin.ModelAdmin):
#     list_display = ('scheduled_date', 'scheduled_time', 'service_center', 'scheduled_by', 'created_at')
#     filter_horizontal = ('bookings',)
#     readonly_fields = ('created_at',)

#     def save_model(self, request, obj, form, change):
#         # Set the scheduler to current admin
#         if not obj.scheduled_by:
#             obj.scheduled_by = request.user
#         super().save_model(request, obj, form, change)
#         # Apply schedule immediately
#         obj.apply_schedule()
#         self.message_user(request, f"Scheduled {obj.bookings.count()} booking(s) on {obj.scheduled_date} at {obj.scheduled_time}.")


@admin.register(ServiceReminder)
class ServiceReminderAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'reminder_type_display', 'scheduled_send_date',
                   'reminder_date', 'is_sent')
    list_filter = ('reminder_type', 'is_sent', 'scheduled_send_date')
    search_fields = ('vehicle__license_plate', 'vehicle__vin', 'message')
    
    def reminder_type_display(self, obj):
        return obj.get_reminder_type_display()
    reminder_type_display.short_description = "Reminder Type"



@admin.register(ContactOrder)
class ContactOrderAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'phone_number',
        'electric_car',
        'status',
        'is_seen',
        'created_at',
    )

    list_filter = ('status', 'is_seen', 'created_at')

    search_fields = ('full_name', 'phone_number', 'electric_car__model_name')

    readonly_fields = ('created_at',)

    # Show alert on admin changelist
    def changelist_view(self, request, extra_context=None):
        new_orders_count = ContactOrder.objects.filter(is_seen=False).count()
        if new_orders_count > 0:
            messages.warning(
                request,
                f"⚠️ You have {new_orders_count} new contact request(s) that needs attention!"
            )
        return super().changelist_view(request, extra_context)

    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, object_id)
        if obj and not obj.is_seen:
            obj.is_seen = True
            obj.save(update_fields=['is_seen'])
        return super().change_view(request, object_id, form_url, extra_context)


# @admin.register(ContactOrder)
# class ContactOrderAdmin(admin.ModelAdmin):
#     list_display = (
#         'full_name',
#         'phone_number',
#         'electric_car',
#         'preferred_contact_time',
#         'status',
#         'created_at',
#     )

#     list_filter = (
#         'status',
#         'preferred_contact_time',
#         'created_at',
#         'electric_car__manufacturer',
#     )

#     search_fields = (
#         'full_name',
#         'phone_number',
#         'electric_car__model_name',
#         'electric_car__manufacturer__name',
#     )

#     readonly_fields = ('created_at',)

#     ordering = ('-created_at',)

#     fieldsets = (
#         ('Customer Information', {
#             'fields': ('full_name', 'phone_number')
#         }),
#         ('Car Information', {
#             'fields': ('electric_car',)
#         }),
#         ('Contact Request', {
#             'fields': ('message', 'preferred_contact_time', 'status')
#         }),
#         ('Metadata', {
#             'fields': ('created_at',)
#         }),
#     )

#     actions = ['mark_as_contacted', 'mark_as_closed']

#     def mark_as_contacted(self, request, queryset):
#         queryset.update(status='contacted')
#         self.message_user(request, "Selected orders marked as contacted.")
#     mark_as_contacted.short_description = "Mark selected orders as Contacted"

#     def mark_as_closed(self, request, queryset):
#         queryset.update(status='closed')
#         self.message_user(request, "Selected orders marked as closed.")
#     mark_as_closed.short_description = "Mark selected orders as Closed"

#     def save_model(self, request, obj, form, change):
#         super().save_model(request, obj, form, change)
#         messages.success(request, "User want's to conatct please respond as soon as possible")



