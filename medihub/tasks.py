from celery import shared_task
import time
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings

@shared_task(bind=True)
def rabbitMQ_tester(self):
    print(f"[{self.request.id}] Task started — sleeping 20s to simulate work")
    time.sleep(20)
    print(f"[{self.request.id}] Task completed")
    return "rabbitMQ_tester done"


@shared_task(bind=True)
def beat_health_check(self):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[BEAT] beat_health_check fired at {now}")
    return f"beat alive at {now}"
    

@shared_task(bind=True)
def beat_log_active_users(self):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    count = User.objects.filter(is_active=True).count()
    print(f"[BEAT] Active users: {count}")
    return f"active users: {count}"


@shared_task(bind=True)
def beat_cleanup_expired_otps(self):
    from django.core.cache import cache
    print(f"[BEAT] OTP cleanup triggered at {datetime.now().strftime('%H:%M:%S')}")
    return "otp cleanup done"


@shared_task(bind=True)
def beat_system_ping(self):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[BEAT] System ping at {now}")
    return f"pong at {now}"

@shared_task(bind=True)
def send_me_email_everyminute(self):
    email = "nightliver000@gmail.com"
    subject = "Your OTP Code"
    message = f"Your OTP is: {49349}. It will expire in 5 minutes."
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
    print(f"[BEAT] Email sent to {email}")
    return f"OTP sent to {email}"