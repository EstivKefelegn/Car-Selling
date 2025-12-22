from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import EmailMessage
from datetime import datetime
from .models import EmailSubscriber, ElectricCar, ContactOrder, ScheduleService, ServiceBooking
from django.core.mail import mail_admins
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=ElectricCar)
def send_inventory_email_on_create(sender, instance, created, **kwargs):
    """
    Send email to all subscribers when a new electric car is created
    """
    if created:
        print(f"New car created: {instance.model_name}. Sending emails to subscribers...")
        
        subscribers = EmailSubscriber.objects.filter(
            subscription_status=EmailSubscriber.SubscriptionStatus.ACTIVE,
            receive_inventory_alerts=True
        )
        
        if not subscribers:
            print("No active subscribers to notify.")
            return
        
        print(f"Preparing to send emails to {subscribers.count()} subscribers")
        send_inventory_alert_to_subscribers(instance, subscribers)


def create_email_body(car):
    """
    Build the body of the inventory email
    """
    year = getattr(car, 'year', 'N/A')
    price = getattr(car, 'price', 'N/A')
    mileage = getattr(car, 'mileage', 'N/A')
    condition = getattr(car, 'condition', 'New')
    location = getattr(car, 'location', 'Available')
    description = getattr(car, 'description', 'Check out this amazing vehicle!')
    features = getattr(car, 'features', '• Well-maintained\n• Excellent condition\n• Ready for immediate delivery')
    
    if isinstance(price, (int, float)):
        price_formatted = f"${price:,.2f}"
    else:
        price_formatted = str(price)
    
    if isinstance(mileage, (int, float)):
        mileage_formatted = f"{mileage:,} miles"
    else:
        mileage_formatted = str(mileage)
    
    body = f"""NEW INVENTORY ALERT!

Dear Valued Subscriber,

We're excited to announce that we've just added a new vehicle to our inventory!

🚗 VEHICLE DETAILS:
• Model: {car.model_name}
• Year: {year}
• Price: {price_formatted}
• Mileage: {mileage_formatted}
• Condition: {condition}
• Location: {location}

📝 DESCRIPTION:
{description}

🔧 ADDITIONAL FEATURES:
{features}

📍 VISIT US:
Come see this vehicle at our dealership or contact us to schedule a test drive!

📞 CONTACT INFORMATION:
Phone: [YOUR_PHONE_NUMBER]
Email: [YOUR_CONTACT_EMAIL]
Address: [YOUR_ADDRESS]

⏰ ACT FAST!
Great deals don't last long. Contact us today before this vehicle is gone!

---
You're receiving this email because you subscribed to our inventory alerts.
To unsubscribe from future alerts, please visit: [UNSUBSCRIBE_LINK]

Thank you for being a valued customer!

Best regards,
Etiopikar Team
"""
    return body


def send_inventory_alert_to_subscribers(car, subscribers):
    subject = f"🚗 New Car Alert: {car.model_name}"
    body = create_email_body(car)  # now this function exists
    recipient_emails = [s.email for s in subscribers]

    for email in recipient_emails:
        try:
            msg = EmailMessage(
                subject=subject,
                body=body,
                from_email=settings.EMAIL_HOST_USER,  # must match SMTP user
                to=[email],
            )
            msg.send(fail_silently=False)
            print(f"Sent alert for {car.model_name} to {email}")
        except Exception as e:
            print(f"Failed to send alert to {email}: {e}")


@receiver(post_save, sender=ContactOrder)
def notify_admin_on_order(sender, instance, created, **kwargs):
    if created:
        mail_admins(
            subject="New Contact Order",
            message=f"""
                New contact request received.

                Name: {instance.full_name}
                Phone: {instance.phone_number}
                Car: {instance.electric_car}
                Preferred Time: {instance.preferred_contact_time}
            """
        )


# NEW SIGNALS FOR SCHEDULESERVICE
@receiver(post_save, sender=ScheduleService)
def apply_schedule_on_save(sender, instance, created, **kwargs):
    """
    Apply schedule automatically when ScheduleService is created
    """
    if created:
        print(f"DEBUG: New ScheduleService created (ID: {instance.id})")
        print(f"DEBUG: Scheduled for {instance.scheduled_date} at {instance.scheduled_time}")
        
        # Check if there are any bookings
        booking_count = instance.bookings.count()
        print(f"DEBUG: Number of bookings: {booking_count}")
        
        if booking_count > 0:
            instance.apply_schedule()
            print(f"DEBUG: Schedule applied to {booking_count} bookings")
        else:
            print(f"DEBUG: No bookings to schedule")


@receiver(m2m_changed, sender=ScheduleService.bookings.through)
def apply_schedule_on_bookings_changed(sender, instance, action, **kwargs):
    """
    Apply schedule when bookings are added or changed
    """
    if action in ['post_add', 'post_remove']:
        print(f"DEBUG: Bookings changed for ScheduleService {instance.id}")
        print(f"DEBUG: Action: {action}")
        
        # Re-apply schedule to update all bookings
        instance.apply_schedule()
        
        # Update the instance to track changes
        instance.save()


# Optional: Signal to notify customers when their booking is scheduled
@receiver(post_save, sender=ServiceBooking)
def notify_on_booking_scheduled(sender, instance, **kwargs):
    """
    Send notification when booking status changes to scheduled
    """
    # Check if this is an update (not a new creation)
    if not instance._state.adding:
        try:
            # Get the previous state from database
            old_instance = ServiceBooking.objects.get(pk=instance.pk)
            old_status = old_instance.status
            new_status = instance.status
            
            # Check if status changed to 'scheduled'
            if old_status != 'scheduled' and new_status == 'scheduled':
                print(f"DEBUG: Booking {instance.booking_number} status changed to scheduled")
                print(f"DEBUG: is_scheduled: {instance.is_scheduled}")
                
                # Find the ScheduleService that scheduled this booking
                schedules = instance.schedules.all()
                if schedules.exists():
                    schedule = schedules.first()
                    print(f"DEBUG: Booked via ScheduleService {schedule.id}")
                    
                    # The email should already be sent by apply_schedule(),
                    # but we can add additional logging or actions here
                    
        except ServiceBooking.DoesNotExist:
            pass  # This is a new booking, not an update


@receiver(post_save, sender=ServiceBooking)
def verify_booking_scheduled_status(sender, instance, created, **kwargs):
    """
    Verify and log the booking scheduling status
    """
    if not created:  
        print(f"DEBUG: Booking {instance.booking_number} saved")
        print(f"DEBUG: - Status: {instance.status}")
        print(f"DEBUG: - is_scheduled: {instance.is_scheduled}")
        print(f"DEBUG: - Service Center: {instance.service_center}")
        
        if instance.status == 'scheduled' and not instance.is_scheduled:
            print(f"WARNING: Booking {instance.booking_number} has status 'scheduled' but is_scheduled=False")
            instance.is_scheduled = True
            instance.save(update_fields=['is_scheduled'])

@receiver(post_save, sender=ServiceBooking)
def notify_service_managers_on_service_created(sender, instance, created, **kwargs):
    """
    Send plain-text email to Service Managers when a service booking is created
    """
    if not created:
        return

    service_managers = User.objects.filter(
        groups__name="Service Handler",
        is_active=True,
        is_staff=True
    ).exclude(email="")

    if not service_managers.exists():
        return

    recipient_emails = service_managers.values_list("email", flat=True)

    subject = f"New Service Request – Booking #{instance.booking_number}"

    message = f"""
A new service request has been created.

BOOKING DETAILS
-------------------------
Booking Number: {instance.booking_number}
Customer Name: {instance.customer}
Customer Email: {instance.customer_email}
Customer Phone: {instance.customer_phone or 'N/A'}

VEHICLE DETAILS
-------------------------
Model: {instance.vehicle.model_name}
VIN: {getattr(instance.vehicle, 'vin', 'N/A')}
Current Odometer: {instance.odometer_reading} km

SERVICE DETAILS
-------------------------
Service Type: {instance.get_service_type_display()}
Preferred Date: {instance.preferred_date}
Preferred Time: {instance.preferred_time_slot}
Priority: {instance.get_priority_display()}
Status: {instance.get_status_display()}

Description:
{instance.service_description or 'No description provided'}

Please log in to the admin panel to review and assign this service.

— Etiopikar System
""".strip()

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=list(recipient_emails),
        fail_silently=False,
    )


@receiver(post_save, sender=ContactOrder)
def notify_order_managers_on_order_created(sender, instance, created, **kwargs):
    """
    Send plain-text email to Order Manager group when a new contact order is created
    """
    if not created:
        return

    order_managers = User.objects.filter(
        groups__name="Order Manager",
        is_active=True,
        is_staff=True
    ).exclude(email="")

    if not order_managers.exists():
        return

    recipient_emails = order_managers.values_list("email", flat=True)

    subject = f"New Contact Order – {instance.full_name}"

    message = f"""
A new contact order has been submitted.

CUSTOMER DETAILS
-------------------------
Name: {instance.full_name}
Phone: {instance.phone_number}

CAR DETAILS
-------------------------
Model: {instance.electric_car.display_name}
Year: {getattr(instance.electric_car, 'year', 'N/A')}
Price: {getattr(instance.electric_car, 'price', 'N/A')}

ORDER DETAILS
-------------------------
Message: {instance.message}
Preferred Contact Time: {instance.get_preferred_contact_time_display()}
Status: {instance.get_status_display()}

Please log in to the admin panel to process this order.

— Etiopikar System
""".strip()

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=list(recipient_emails),
        fail_silently=False,
    )


@receiver(post_save, sender=ScheduleService)
@receiver(m2m_changed, sender=ScheduleService.bookings.through)
def check_and_send_service_reminders(sender, instance, action=None, **kwargs):
    """
    Send reminders when bookings are scheduled via ScheduleService
    """
    try:
        # Only trigger for post_save or when bookings are added
        if action in [None, 'post_add', 'post_remove']:
            # Get the scheduled date from ScheduleService
            scheduled_date = instance.scheduled_date
            today = timezone.now().date()
            
            # Check if scheduled date is today or tomorrow
            for booking in instance.bookings.all():
                if scheduled_date == today and not booking.reminder_sent:
                    send_today_service_plain_email(booking, instance)
                    booking.reminder_sent = True
                    booking.save(update_fields=['reminder_sent'])
                    logger.info(f"Today's reminder sent for booking #{booking.booking_number}")
                
                elif scheduled_date == today + timedelta(days=1) and not booking.follow_up_sent:
                    send_tomorrow_service_plain_email(booking, instance)
                    booking.follow_up_sent = True
                    booking.save(update_fields=['follow_up_sent'])
                    logger.info(f"Tomorrow's reminder sent for booking #{booking.booking_number}")
                    
    except Exception as e:
        logger.error(f"Error sending service reminders: {e}")

def get_scheduled_date_for_booking(booking):
    """
    Get the scheduled date for a booking from ScheduleService
    Returns scheduled_date if booked via ScheduleService, else preferred_date
    """
    # Check if booking is scheduled via ScheduleService
    if booking.is_scheduled and booking.schedules.exists():
        schedule = booking.schedules.first()
        return schedule.scheduled_date
    else:
        # Fall back to preferred_date for manually scheduled bookings
        return booking.preferred_date

def send_today_service_plain_email(booking, schedule=None):
    """
    Send plain text email for today's scheduled service
    """
    if schedule:
        scheduled_date = schedule.scheduled_date
        scheduled_time = schedule.scheduled_time
        service_center = schedule.service_center
    else:
        # Try to get schedule from booking
        schedule = booking.schedules.first() if booking.schedules.exists() else None
        if schedule:
            scheduled_date = schedule.scheduled_date
            scheduled_time = schedule.scheduled_time
            service_center = schedule.service_center
        else:
            # Fall back to booking fields
            scheduled_date = booking.preferred_date
            scheduled_time = booking.preferred_time_slot
            service_center = booking.service_center
    
    subject = f"🔔 Service Appointment Today - Booking #{booking.booking_number}"
    
    message = f"""
Hello {booking.customer},

Your vehicle service appointment is scheduled for TODAY.

APPOINTMENT DETAILS:
────────────────────
Booking Number: {booking.booking_number}
Scheduled Date: {scheduled_date.strftime('%B %d, %Y')}
Scheduled Time: {scheduled_time.strftime('%I:%M %p') if scheduled_time else 'To be confirmed'}
Service Type: {booking.get_service_type_display()}
Vehicle: {booking.vehicle.manufacturer_name} {booking.vehicle.model_name}
Service Center: {service_center.name if service_center else 'To be assigned'}

IMPORTANT REMINDERS:
────────────────────
• Please arrive 15 minutes before your appointment
• Bring your vehicle registration and ID
• Remove personal belongings from your vehicle

CONTACT INFORMATION:
────────────────────
Phone: {getattr(settings, 'SERVICE_PHONE', '+251 11 123 4567')}
Email: {getattr(settings, 'SERVICE_EMAIL', 'service@etiopikar.com')}

If you need to reschedule or have any questions, please contact us.

Safe travels!

The Etiopikar Service Team
"""
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.customer_email],
            fail_silently=False,
        )
        logger.info(f"Today's service email sent to {booking.customer_email}")
    except Exception as e:
        logger.error(f"Failed to send today's service email: {e}")

def send_tomorrow_service_plain_email(booking, schedule=None):
    """
    Send plain text email for tomorrow's scheduled service
    """
    if schedule:
        scheduled_date = schedule.scheduled_date
        scheduled_time = schedule.scheduled_time
    else:
        # Try to get schedule from booking
        schedule = booking.schedules.first() if booking.schedules.exists() else None
        if schedule:
            scheduled_date = schedule.scheduled_date
            scheduled_time = schedule.scheduled_time
        else:
            # Fall back to booking fields
            scheduled_date = booking.preferred_date
            scheduled_time = booking.preferred_time_slot
    
    subject = f"⏰ Service Appointment Tomorrow - Booking #{booking.booking_number}"
    
    message = f"""
Hello {booking.customer},

Friendly reminder: Your vehicle service appointment is scheduled for TOMORROW.

APPOINTMENT DETAILS:
────────────────────
Booking Number: {booking.booking_number}
Scheduled Date: {scheduled_date.strftime('%B %d, %Y')}
Scheduled Time: {scheduled_time.strftime('%I:%M %p') if scheduled_time else 'To be confirmed'}
Service Type: {booking.get_service_type_display()}
Vehicle: {booking.vehicle.manufacturer_name} {booking.vehicle.model_name}

REMINDERS:
──────────
• Please arrive 15 minutes before your appointment
• Bring your vehicle registration and ID
• Remove personal belongings from your vehicle

CONTACT INFORMATION:
────────────────────
Phone: {getattr(settings, 'SERVICE_PHONE', '+251 11 123 4567')}
Email: {getattr(settings, 'SERVICE_EMAIL', 'service@etiopikar.com')}

If you need to reschedule or have any questions, please contact us.

We look forward to serving you!

The Etiopikar Service Team
"""
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.customer_email],
            fail_silently=False,
        )
        logger.info(f"Tomorrow's service email sent to {booking.customer_email}")
    except Exception as e:
        logger.error(f"Failed to send tomorrow's service email: {e}")


def send_daily_service_reminders():
    """
    Function to be called by cron job daily
    Check all scheduled bookings and send reminders
    """
    try:
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        
        # Find all ScheduleServices with dates today or tomorrow
        today_schedules = ScheduleService.objects.filter(
            scheduled_date=today
        ).prefetch_related('bookings')
        
        tomorrow_schedules = ScheduleService.objects.filter(
            scheduled_date=tomorrow
        ).prefetch_related('bookings')
        
        # Process today's scheduled services
        logger.info(f"Found {today_schedules.count()} schedules for today")
        for schedule in today_schedules:
            for booking in schedule.bookings.all():
                if not booking.reminder_sent and booking.status == 'scheduled':
                    try:
                        send_today_service_plain_email(booking, schedule)
                        booking.reminder_sent = True
                        booking.save(update_fields=['reminder_sent'])
                        logger.info(f"Today's reminder sent for booking #{booking.booking_number}")
                    except Exception as e:
                        logger.error(f"Failed to send today's reminder for booking #{booking.booking_number}: {e}")
        
        # Process tomorrow's scheduled services
        logger.info(f"Found {tomorrow_schedules.count()} schedules for tomorrow")
        for schedule in tomorrow_schedules:
            for booking in schedule.bookings.all():
                if not booking.follow_up_sent and booking.status == 'scheduled':
                    try:
                        send_tomorrow_service_plain_email(booking, schedule)
                        booking.follow_up_sent = True
                        booking.save(update_fields=['follow_up_sent'])
                        logger.info(f"Tomorrow's reminder sent for booking #{booking.booking_number}")
                    except Exception as e:
                        logger.error(f"Failed to send tomorrow's reminder for booking #{booking.booking_number}: {e}")
        
        # Also check individual bookings not scheduled via ScheduleService
        # (for backward compatibility)
        individual_today_bookings = ServiceBooking.objects.filter(
            preferred_date=today,
            reminder_sent=False,
            status__in=['scheduled', 'confirmed'],
            is_scheduled=False  # Not scheduled via ScheduleService
        )
        
        for booking in individual_today_bookings:
            try:
                send_today_service_plain_email(booking, None)
                booking.reminder_sent = True
                booking.save(update_fields=['reminder_sent'])
                logger.info(f"Today's reminder sent for individual booking #{booking.booking_number}")
            except Exception as e:
                logger.error(f"Failed to send today's reminder for individual booking #{booking.booking_number}: {e}")
        
        individual_tomorrow_bookings = ServiceBooking.objects.filter(
            preferred_date=tomorrow,
            follow_up_sent=False,
            status__in=['scheduled', 'confirmed'],
            is_scheduled=False
        )
        
        for booking in individual_tomorrow_bookings:
            try:
                send_tomorrow_service_plain_email(booking, None)
                booking.follow_up_sent = True
                booking.save(update_fields=['follow_up_sent'])
                logger.info(f"Tomorrow's reminder sent for individual booking #{booking.booking_number}")
            except Exception as e:
                logger.error(f"Failed to send tomorrow's reminder for individual booking #{booking.booking_number}: {e}")
                
    except Exception as e:
        logger.error(f"Error in daily service reminders: {e}")


@receiver(post_save, sender=ScheduleService)
def send_schedule_confirmation_on_create(sender, instance, created, **kwargs):
    """
    Send confirmation emails when a new ScheduleService is created
    """
    if created:
        for booking in instance.bookings.all():
            try:
                send_schedule_confirmation_plain_email(booking, instance)
                logger.info(f"Schedule confirmation sent for booking #{booking.booking_number}")
            except Exception as e:
                logger.error(f"Failed to send schedule confirmation for booking #{booking.booking_number}: {e}")

def send_schedule_confirmation_plain_email(booking, schedule):
    """
    Send plain text schedule confirmation email
    """
    subject = f"✅ Service Appointment Scheduled - #{booking.booking_number}"
    
    message = f"""
Hello {booking.customer},

Your vehicle service has been scheduled.

SCHEDULED APPOINTMENT:
───────────────────────
Booking Number: {booking.booking_number}
Scheduled Date: {schedule.scheduled_date.strftime('%B %d, %Y')}
Scheduled Time: {schedule.scheduled_time.strftime('%I:%M %p')}
Service Type: {booking.get_service_type_display()}
Vehicle: {booking.vehicle.manufacturer_name} {booking.vehicle.model_name}
Service Center: {schedule.service_center.name if schedule.service_center else 'To be assigned'}

REMINDERS:
──────────
• Please arrive 15 minutes before your appointment
• Bring your vehicle registration and ID
• Remove personal belongings from your vehicle
• Service may take 3-6 hours depending on complexity

CONTACT INFORMATION:
────────────────────
Phone: {getattr(settings, 'SERVICE_PHONE', '+251 11 123 4567')}
Email: {getattr(settings, 'SERVICE_EMAIL', 'service@etiopikar.com')}

If you need to reschedule or have any questions, please contact us at least 24 hours in advance.

We look forward to serving you!

The Etiopikar Service Team
"""
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[booking.customer_email],
        fail_silently=False,
    )


@receiver(post_save, sender=ServiceBooking)
def send_completion_email_on_finish(sender, instance, **kwargs):
    """
    Send completion email when service is marked as completed
    """
    try:
        if not instance._state.adding:  # Not a new instance
            old_instance = ServiceBooking.objects.get(pk=instance.pk)
            
            # Check if status changed to completed
            if old_instance.status != 'completed' and instance.status == 'completed':
                send_service_completion_plain_email(instance)
                logger.info(f"Completion email sent for booking #{instance.booking_number}")
    
    except ServiceBooking.DoesNotExist:
        pass  # New booking
    except Exception as e:
        logger.error(f"Failed to send completion email: {e}")

def send_service_completion_plain_email(booking):
    """
    Send plain text service completion email
    """
    # Get schedule info if available
    schedule = booking.schedules.first() if booking.schedules.exists() else None
    
    subject = f"✅ Service Completed - #{booking.booking_number}"
    
    message = f"""
Hello {booking.customer},

Your vehicle service has been completed successfully.

SERVICE COMPLETION DETAILS:
───────────────────────────
Booking Number: {booking.booking_number}
Completion Date: {booking.completed_at.strftime('%B %d, %Y') if booking.completed_at else 'Today'}
Service Type: {booking.get_service_type_display()}
Vehicle: {booking.vehicle.manufacturer_name} {booking.vehicle.model_name}
Final Odometer: {booking.final_odometer} km
Technician: {booking.assigned_technician.get_full_name() if booking.assigned_technician else 'Service Team'}

SERVICE REPORT:
───────────────
{booking.service_report or 'Service completed successfully.'}

COST SUMMARY:
─────────────
{ 'Total Cost: $' + str(booking.total_cost) if booking.total_cost else 'Warranty Covered' if booking.warranty_covered else 'To be billed' }

NEXT SERVICE:
─────────────
Please check your vehicle manual for the next recommended service interval.

PICKUP INFORMATION:
───────────────────
Your vehicle is ready for pickup at {booking.service_center.name if booking.service_center else 'our service center'}.

CONTACT INFORMATION:
────────────────────
Phone: {getattr(settings, 'SERVICE_PHONE', '+251 11 123 4567')}
Email: {getattr(settings, 'SERVICE_EMAIL', 'service@etiopikar.com')}

Thank you for choosing Etiopikar!

The Etiopikar Service Team
"""
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[booking.customer_email],
        fail_silently=False,
    )