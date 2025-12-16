from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin
from .models import (
    AboutUs, TeamMember, DealershipPhoto,
    Event, EventCategory, EventTag, EventImage,
    EventSpeaker, EventSchedule, EventRegistration,
    EventWaitlist, News
)


class CarSalesAdminSite(AdminSite):
    site_header = "Etiopikar Electric Cars Administration"
    site_title = "Etiopikar EV Admin"
    index_title = "Welcome to Etiopikar Electric Car Sales Admin"


@admin.register(AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    list_display = ('dealership_name', 'city', 'phone_number', 'email', 'is_active')
    list_filter = ('is_active', 'city', 'country')
    search_fields = ('dealership_name', 'city', 'email', 'phone_number')
    readonly_fields = ('created_at', 'updated_at', 'google_maps_link')
    fieldsets = (
        ('Basic Information', {
            'fields': ('dealership_name', 'tagline', 'logo', 'description')
        }),
        ('Location Information', {
            'fields': ('address', 'city', 'state_province', 'postal_code', 'country',
                      'latitude', 'longitude', 'map_zoom_level', 'google_maps_link')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'secondary_phone', 'email', 'support_email', 'website')
        }),
        ('Business Hours', {
            'fields': (
                ('monday_open', 'monday_close'),
                ('tuesday_open', 'tuesday_close'),
                ('wednesday_open', 'wednesday_close'),
                ('thursday_open', 'thursday_close'),
                ('friday_open', 'friday_close'),
                ('saturday_open', 'saturday_close'),
                ('sunday_open', 'sunday_close'),
            )
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url', 'youtube_url')
        }),
        ('Additional Information', {
            'fields': ('mission_statement', 'vision_statement', 'core_values', 
                      'history', 'services_offered', 'brands_carried')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    
    def google_maps_link(self, obj):
        if obj.latitude and obj.longitude:
            return format_html(
                '<a href="{}" target="_blank">Open in Google Maps</a>',
                obj.google_maps_url
            )
        return "Coordinates not set"
    google_maps_link.short_description = "Google Maps Link"
    
    actions = ['activate', 'deactivate']
    
    def activate(self, request, queryset):
        queryset.update(is_active=True)
    activate.short_description = "Activate selected"
    
    def deactivate(self, request, queryset):
        queryset.update(is_active=False)
    deactivate.short_description = "Deactivate selected"


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'position_display', 'about_us', 'years_experience', 'is_active')
    list_filter = ('position', 'is_active', 'about_us')
    search_fields = ('full_name', 'email', 'phone')
    list_editable = ('is_active',)
    
    def position_display(self, obj):
        return obj.display_position
    position_display.short_description = 'Position'


@admin.register(DealershipPhoto)
class DealershipPhotoAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'caption', 'photo_type', 'about_us', 'is_active')
    list_filter = ('photo_type', 'is_active', 'about_us')
    search_fields = ('caption',)
    
    def thumbnail(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" />', obj.photo.url)
        return "No Image"
    thumbnail.short_description = 'Thumbnail'

admin.site.site_header = "Etiopikar Electric Cars Administration"
admin.site.site_title = "Etiopikar EV Admin"
admin.site.index_title = "Welcome to Etiopikar Electric Car Sales Admin"


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'display_order', 'color_display']
    list_editable = ['display_order']
    prepopulated_fields = {'slug': ['name']}
    
    def color_display(self, obj):
        return format_html(
            '<span style="display: inline-block; width: 20px; height: 20px; '
            'background-color: {}; border-radius: 3px;"></span> {}',
            obj.color, obj.color
        )
    color_display.short_description = 'Color'

@admin.register(EventTag)
class EventTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ['name']}

class EventImageInline(admin.TabularInline):
    model = EventImage
    extra = 1
    fields = ['image', 'caption', 'alt_text', 'display_order']

class EventSpeakerInline(admin.TabularInline):
    model = EventSpeaker
    extra = 1
    fields = ['name', 'title', 'company', 'photo', 'display_order']

class EventScheduleInline(admin.TabularInline):
    model = EventSchedule
    extra = 1
    fields = ['day', 'start_time', 'end_time', 'title', 'location']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'event_type', 'start_date', 'end_date',
        'status', 'is_featured', 'views', 'current_attendees'
    ]
    list_filter = [
        'status', 'event_type', 'is_featured', 'is_virtual',
        'requires_registration', 'start_date'
    ]
    search_fields = ['title', 'description', 'venue_name', 'city']
    prepopulated_fields = {'slug': ['title']}
    readonly_fields = ['views', 'current_attendees', 'created_at', 'updated_at']
    date_hierarchy = 'start_date'
    filter_horizontal = ['tags']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title', 'slug', 'description', 'detailed_description',
                'event_type', 'category', 'tags'
            )
        }),
        ('Date & Time', {
            'fields': (
                'start_date', 'end_date', 'timezone'
            )
        }),
        ('Location', {
            'fields': (
                'is_virtual', 'venue_name', 'address', 'city',
                'state', 'country', 'zip_code',
                'virtual_platform', 'virtual_link',
                'virtual_meeting_id', 'virtual_passcode'
            )
        }),
        ('Registration', {
            'fields': (
                'requires_registration', 'is_free', 'registration_link',
                'max_attendees', 'current_attendees', 'price', 'currency'
            )
        }),
        ('Media', {
            'fields': (
                'cover_image', 'banner_image'
            )
        }),
        ('Status & Visibility', {
            'fields': (
                'status', 'is_featured', 'is_private', 'published_at'
            )
        }),
        ('Organizer Information', {
            'fields': (
                'organizer', 'contact_person', 'contact_email', 'contact_phone'
            )
        }),
        ('SEO', {
            'fields': (
                'meta_title', 'meta_description', 'meta_keywords'
            )
        }),
        ('Statistics', {
            'fields': (
                'views', 'created_at', 'updated_at'
            )
        }),
    )
    
    inlines = [EventImageInline, EventSpeakerInline, EventScheduleInline]
    
    actions = ['mark_as_featured', 'mark_as_upcoming', 'duplicate_event']
    
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} events marked as featured.')
    mark_as_featured.short_description = "Mark selected events as featured"
    
    def mark_as_upcoming(self, request, queryset):
        updated = queryset.update(status='upcoming')
        self.message_user(request, f'{updated} events marked as upcoming.')
    mark_as_upcoming.short_description = "Mark selected events as upcoming"
    
    def duplicate_event(self, request, queryset):
        for event in queryset:
            event.pk = None
            event.title = f"{event.title} (Copy)"
            event.slug = f"{event.slug}-copy-{timezone.now().timestamp()}"
            event.save()
        self.message_user(request, f'{queryset.count()} events duplicated.')
    duplicate_event.short_description = "Duplicate selected events"

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'email', 'event', 'registration_date',
        'is_confirmed', 'checked_in', 'payment_status'
    ]
    list_filter = [
        'is_confirmed', 'checked_in', 'payment_status',
        'event', 'registration_date'
    ]
    search_fields = ['full_name', 'email', 'company', 'event__title']
    readonly_fields = ['registration_date', 'checkin_time']
    date_hierarchy = 'registration_date'
    
    actions = ['confirm_registrations', 'mark_as_checked_in']
    
    def confirm_registrations(self, request, queryset):
        updated = queryset.update(is_confirmed=True)
        self.message_user(request, f'{updated} registrations confirmed.')
    confirm_registrations.short_description = "Confirm selected registrations"
    
    def mark_as_checked_in(self, request, queryset):
        for registration in queryset:
            registration.checked_in = True
            registration.checkin_time = timezone.now()
            registration.save()
        self.message_user(request, f'{queryset.count()} attendees checked in.')
    mark_as_checked_in.short_description = "Mark selected as checked in"

@admin.register(EventWaitlist)
class EventWaitlistAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'event', 'joined_at', 'notified']
    list_filter = ['notified', 'event', 'joined_at']
    search_fields = ['full_name', 'email', 'event__title']
    readonly_fields = ['joined_at']
    date_hierarchy = 'joined_at'

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'is_featured', 'author', 'formatted_published_date', 'image_preview']
    list_filter = ['status', 'is_featured', 'created_at']
    search_fields = ['title', 'description', 'content']
    prepopulated_fields = {'slug': ['title']}
    readonly_fields = ['created_at', 'updated_at', 'image_preview']
    date_hierarchy = 'published_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title', 'slug', 'description', 'content',
                'image', 'image_preview'
            )
        }),
        ('Status & Visibility', {
            'fields': (
                'status', 'is_featured', 'published_at'
            )
        }),
        ('Author Information', {
            'fields': (
                'author',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def formatted_published_date(self, obj):
        return obj.formatted_published_date
    formatted_published_date.short_description = 'Published Date'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'
    
    actions = ['mark_as_published', 'mark_as_featured']
    
    def mark_as_published(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, f'{updated} news articles published.')
    mark_as_published.short_description = "Mark selected as published"
    
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} news articles marked as featured.')
    mark_as_featured.short_description = "Mark selected as featured"
