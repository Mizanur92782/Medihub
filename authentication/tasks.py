from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_otp_email_task(email, otp):
    subject = "Your OTP Code"
    message = f"Your OTP is: {otp}. It will expire in 5 minutes."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
    return f"OTP sent to {email}"


@shared_task
def send_password_reset_otp_task(email, otp):
    subject = "Password Reset OTP"
    message = f"Your password reset OTP is: {otp}. It will expire in 5 minutes."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
    return f"Password reset OTP sent to {email}"

