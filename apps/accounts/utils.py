import random
import string
from django.core.mail import send_mail
from django.conf import settings

def generate_otp():
    """Generates a 6-digit numeric OTP."""
    return ''.join(random.choices(string.digits, k=6))

def send_2fa_otp_email(user, otp):
    """Sends the OTP code to the user's institution email."""
    subject = "Your URMS Login Verification Code"
    message = f"Hello {user.first_name or user.username},\n\nYour 2FA verification code is: {otp}\n\nThis code will expire in 10 minutes.\n\nThank you,\nURMS Security Team."
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )
