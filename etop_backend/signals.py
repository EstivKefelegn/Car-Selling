# signals.py
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import EmailMessage
from datetime import datetime
from .models import EmailSubscriber, ElectricCar, ContactOrder, ScheduleService, ServiceBooking
from django.core.mail import mail_admins
from django.core.mail import send_mail

# Your existing signals...

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

    # Get Order Manager users
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
