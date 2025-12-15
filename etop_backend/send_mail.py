from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import ssl

def send_email_secure(subject, sender, recipients, cc, body, smtp_server, smtp_port):
    try:
        context = ssl.create_default_context()
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)
        msg['Cc'] = ', '.join(cc)
        msg.attach(MIMEText(body, 'plain'))
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(sender, "your-password")
            server.sendmail(sender, recipients + cc, msg.as_string())
        print("Secure email sent successfully!")
    except smtplib.SMTPException as e:
        print(f"SMTP error occurred: {e}")
    except Exception as e:
        print(f"General error: {e}")


        