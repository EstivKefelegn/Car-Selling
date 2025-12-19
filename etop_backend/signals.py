# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import EmailMessage
from datetime import datetime
from .models import EmailSubscriber, ElectricCar

@receiver(post_save, sender=ElectricCar)
def send_inventory_email_on_create(sender, instance, created, **kwargs):
    """
    Send email to all subscribers when a new electric car is created
    """
    if created:
        print(f"📢 New car created: {instance.model_name}. Sending emails to subscribers...")
        
        subscribers = EmailSubscriber.objects.filter(
            subscription_status=EmailSubscriber.SubscriptionStatus.ACTIVE,
            receive_inventory_alerts=True
        )
        
        if not subscribers:
            print("ℹ️ No active subscribers to notify.")
            return
        
        print(f"📧 Preparing to send emails to {subscribers.count()} subscribers")
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
