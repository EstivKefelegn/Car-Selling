# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import ssl
from datetime import datetime
from .models import EmailSubscriber, ElectricCar 

@receiver(post_save, sender=ElectricCar)
def send_inventory_email_on_create(sender, instance, created, **kwargs):
    """
    Send email to all subscribers when a new electric car is created
    """
    if created and instance.is_active:
        print(f"📢 New car created: {instance.title}. Sending emails to subscribers...")
        
        # Get all active subscribers
        subscribers = EmailSubscriber.objects.filter(
            subscription_status=EmailSubscriber.SubscriptionStatus.ACTIVE,
            receive_inventory_alerts=True
        )
        
        if not subscribers:
            print("ℹ️ No active subscribers to notify.")
            return
        
        print(f"📧 Preparing to send emails to {subscribers.count()} subscribers")
        
        # Send emails
        send_inventory_alert_to_subscribers(instance, subscribers)


def send_inventory_alert_to_subscribers(car, subscribers):
    """
    Send inventory alert email to all subscribers
    """
    subject = f"🚗 New Car Alert: {car.title}"
    
    # Create the email body
    body = create_email_body(car)
    
    # SMTP configuration
    smtp_server = getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com')
    smtp_port = getattr(settings, 'EMAIL_PORT', 465)
    sender_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@yourdealership.com')
    email_password = getattr(settings, 'EMAIL_HOST_PASSWORD', 'your-password')
    
    # Get all recipient emails
    recipient_emails = [subscriber.email for subscriber in subscribers]
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = ', '.join(recipient_emails)  # Send as BCC for privacy
        
        # Add email body
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to SMTP server and send
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(sender_email, email_password)
            server.sendmail(sender_email, recipient_emails, msg.as_string())
        
        # Log success
        print(f"Successfully sent inventory alert for '{car.title}' to {len(recipient_emails)} subscribers")
        log_notification(car, len(recipient_emails), True)
        
    except smtplib.SMTPException as e:
        print(f" SMTP error: {e}")
        log_notification(car, len(recipient_emails), False, str(e))
    except Exception as e:
        print(f" General error: {e}")
        log_notification(car, len(recipient_emails), False, str(e))


def create_email_body(car):
    """
    Create the email body content
    """
    # Get car details with fallbacks
    year = getattr(car, 'year', 'N/A')
    price = getattr(car, 'price', 'N/A')
    mileage = getattr(car, 'mileage', 'N/A')
    condition = getattr(car, 'condition', 'New')
    location = getattr(car, 'location', 'Available')
    
    # Format price if it's a number
    if isinstance(price, (int, float)):
        price_formatted = f"${price:,.2f}"
    else:
        price_formatted = str(price)
    
    # Format mileage if it's a number
    if isinstance(mileage, (int, float)):
        mileage_formatted = f"{mileage:,} miles"
    else:
        mileage_formatted = str(mileage)
    
    # Create the body WITHOUT f-string for the template
    # Use .format() or concatenation instead
    description = getattr(car, 'description', 'Check out this amazing vehicle!')
    features = getattr(car, 'features', '• Well-maintained\n• Excellent condition\n• Ready for immediate delivery')
    
    body = f"""NEW INVENTORY ALERT!

Dear Valued Subscriber,

We're excited to announce that we've just added a new vehicle to our inventory!

🚗 VEHICLE DETAILS:
-------------------
• Model: {car.title}
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
To unsubscribe from future alerts, please visit: 

Thank you for being a valued customer!

Best regards,
Etiopikar Team
"""
    return body


def log_notification(car, subscriber_count, success=True, error_message=''):
    """
    Log the notification attempt
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    status = "SUCCESS" if success else "FAILED"
    log_entry = f"[{timestamp}] {status} - Sent alert for '{car.title}' to {subscriber_count} subscribers"
    
    if not success:
        log_entry += f" | Error: {error_message}"
    
    print(log_entry)
    
    # Optional: Save to a log file
    with open('inventory_notifications.log', 'a') as f:
        f.write(log_entry + '\n')