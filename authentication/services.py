import logging
import hashlib
import random
from django.core.cache import cache
from django.conf import settings
from django.db import transaction, DatabaseError
from authentication.models import User
from profiles.models.doctor_prof_mod import Doctor
from .tasks import send_otp_email_task

logger = logging.getLogger(__name__)


class AuthEmailService:

    CACHE_PREFIX       = 'auth:otp'
    SIGNUP_DATA_PREFIX = 'auth:signup_data'

    # ---------------------------
    # 1. KEY GENERATOR
    # ---------------------------
    @classmethod
    def make_auth_cache_key(cls, *args):
        raw = ':'.join(map(str, args))
        return hashlib.sha256(raw.encode()).hexdigest()

    # ---------------------------
    # 2. OTP GENERATOR
    # ---------------------------
    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))

    @classmethod
    def hash_otp(cls, otp):
        return hashlib.sha256(otp.encode()).hexdigest()

    # ---------------------------
    # 3. SET OTP + CACHE SIGNUP DATA + CELERY EMAIL
    # ---------------------------
    @classmethod
    def set_otp(cls, email, signup_data: dict):
        otp     = cls.generate_otp()
        timeout = getattr(settings, 'OTP_TIMEOUT', 300)

        # cache hashed OTP
        otp_key = cls.make_auth_cache_key(cls.CACHE_PREFIX, email)
        cache.set(otp_key, cls.hash_otp(otp), timeout=timeout)

        # cache full signup data (FK ids stored as integers)
        data_key = cls.make_auth_cache_key(cls.SIGNUP_DATA_PREFIX, email)
        cache.set(data_key, signup_data, timeout=timeout)

        send_otp_email_task.delay(email, otp)

        logger.info('otp_set', extra={'email': email, 'expires_in': timeout})
        return {'email': email, 'expires_in': timeout, 'message': 'OTP sent to email'}

    # ---------------------------
    # 4. GET / INVALIDATE OTP
    # ---------------------------
    @classmethod
    def get_otp(cls, email):
        key = cls.make_auth_cache_key(cls.CACHE_PREFIX, email)
        return cache.get(key)

    @classmethod
    def invalidate_otp(cls, email):
        otp_key  = cls.make_auth_cache_key(cls.CACHE_PREFIX, email)
        data_key = cls.make_auth_cache_key(cls.SIGNUP_DATA_PREFIX, email)
        cache.delete(otp_key)
        cache.delete(data_key)

    # ---------------------------
    # 5. GET SIGNUP DATA
    # ---------------------------
    @classmethod
    def get_signup_data(cls, email):
        key = cls.make_auth_cache_key(cls.SIGNUP_DATA_PREFIX, email)
        return cache.get(key)

    # ---------------------------
    # 6. VERIFY OTP
    # ---------------------------
    @classmethod
    def verify_otp(cls, email, input_otp):
        cached_otp = cls.get_otp(email)

        if not cached_otp:
            return {'status': False, 'message': 'OTP expired or not found'}

        if cached_otp == cls.hash_otp(input_otp):
            return {'status': True, 'message': 'OTP verified successfully'}

        return {'status': False, 'message': 'Invalid OTP'}


class ProfileCreationService:

    @staticmethod
    def create_doctor_profile(signup_data: dict) -> User:
        """
        Creates User + Doctor atomically from cached signup data.
        Must only be called after OTP is verified.
        Raises on failure — caller handles and returns HTTP response.
        """
        email    = signup_data.pop('email')
        password = signup_data.pop('password')
        signup_data.pop('password2', None)

        logger.info('profile_creation_started', extra={'email': email})

        try:
            with transaction.atomic():
                user   = User.objects.create_user(email=email, password=password)
                doctor = Doctor.objects.create(user=user, **signup_data)

            logger.info(
                'profile_creation_success',
                extra={'email': email, 'user_id': user.id, 'doctor_id': doctor.id},
            )
            return user

        except DatabaseError:
            logger.error('profile_creation_db_error', extra={'email': email}, exc_info=True)
            raise

        except Exception:
            logger.critical('profile_creation_unexpected_error', extra={'email': email}, exc_info=True)
            raise
