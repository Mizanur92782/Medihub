import logging
import hashlib
import random
from django.core.cache import cache
from django.conf import settings
from django.db import transaction, DatabaseError
from authentication.models import User
from profiles.models.doctor_prof_mod import Doctor
from profiles.models.user_prof_mod import RegularUserProfile
from profiles.models.blood_donor_mod import BloodDonor
from profiles.models.ambulance_prof_mod import AmbulanceProfile
from profiles.models.pharmacy_prof_mod import PharmacyProfile
from profiles.models.diagnostic_prof_mod import DiagnosticProfile
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
    def _base_create(email, password, signup_data, profile_model, log_key):
        try:
            with transaction.atomic():
                user    = User.objects.create_user(email=email, password=password)
                profile = profile_model.objects.create(user=user, **signup_data)
            logger.info(f'{log_key}_success', extra={'email': email, 'user_id': user.id, 'profile_id': profile.id})
            return user
        except DatabaseError:
            logger.error(f'{log_key}_db_error', extra={'email': email}, exc_info=True)
            raise
        except Exception:
            logger.critical(f'{log_key}_unexpected_error', extra={'email': email}, exc_info=True)
            raise

    @staticmethod
    def _extract_credentials(signup_data: dict):
        email    = signup_data.pop('email')
        password = signup_data.pop('password')
        signup_data.pop('password2', None)
        return email, password

    @classmethod
    def create_doctor_profile(cls, signup_data: dict) -> User:
        email, password = cls._extract_credentials(signup_data)
        logger.info('profile_creation_started', extra={'email': email, 'type': 'doctor'})
        return cls._base_create(email, password, signup_data, Doctor, 'doctor_profile_creation')

    @classmethod
    def create_user_profile(cls, signup_data: dict) -> User:
        email, password = cls._extract_credentials(signup_data)
        logger.info('profile_creation_started', extra={'email': email, 'type': 'user'})
        return cls._base_create(email, password, signup_data, RegularUserProfile, 'user_profile_creation')

    @classmethod
    def create_blood_donor_profile(cls, signup_data: dict) -> User:
        email, password = cls._extract_credentials(signup_data)
        logger.info('profile_creation_started', extra={'email': email, 'type': 'blood_donor'})
        with transaction.atomic():
            try:
                user   = User.objects.create_user(email=email, password=password)
                user.is_blood_donor = True
                user.save(update_fields=['is_blood_donor'])
                profile = BloodDonor.objects.create(user=user, **signup_data)
                logger.info('blood_donor_profile_creation_success', extra={'email': email, 'user_id': user.id, 'profile_id': profile.id})
                return user
            except DatabaseError:
                logger.error('blood_donor_profile_creation_db_error', extra={'email': email}, exc_info=True)
                raise
            except Exception:
                logger.critical('blood_donor_profile_creation_unexpected_error', extra={'email': email}, exc_info=True)
                raise

    @classmethod
    def create_ambulance_profile(cls, signup_data: dict) -> User:
        email, password = cls._extract_credentials(signup_data)
        logger.info('profile_creation_started', extra={'email': email, 'type': 'ambulance'})
        return cls._base_create(email, password, signup_data, AmbulanceProfile, 'ambulance_profile_creation')

    @classmethod
    def create_pharmacy_profile(cls, signup_data: dict) -> User:
        email, password = cls._extract_credentials(signup_data)
        logger.info('profile_creation_started', extra={'email': email, 'type': 'pharmacy'})
        return cls._base_create(email, password, signup_data, PharmacyProfile, 'pharmacy_profile_creation')

    @classmethod
    def create_diagnostic_profile(cls, signup_data: dict) -> User:
        email, password = cls._extract_credentials(signup_data)
        logger.info('profile_creation_started', extra={'email': email, 'type': 'diagnostic'})
        return cls._base_create(email, password, signup_data, DiagnosticProfile, 'diagnostic_profile_creation')
