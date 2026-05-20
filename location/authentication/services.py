import logging
import hashlib
import random
from django.core.cache import cache
from django.conf import settings
from django.db import transaction, DatabaseError
from django.contrib.auth import authenticate
from cache.manager import CacheManager
from cache.ttl import CacheTTL
from rest_framework_simplejwt.tokens import RefreshToken
from authentication.models import User
from profiles.models.doctor_prof_mod import Doctor
from profiles.models.user_prof_mod import RegularUserProfile
from profiles.models.blood_donor_mod import BloodDonor
from profiles.models.ambulance_prof_mod import AmbulanceProfile
from profiles.models.pharmacy_prof_mod import PharmacyProfile
from profiles.models.diagnostic_prof_mod import DiagnosticProfile
from .tasks import send_otp_email_task, send_password_reset_otp_task

logger = logging.getLogger(__name__)


class AuthEmailService:
    CACHE_PREFIX = 'signup:email_verification'
    SIGNUP_DATA_PREFIX = 'signup:data'

    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))

    @staticmethod
    def hash_otp(value):
        return hashlib.sha256(value.encode()).hexdigest()

    @classmethod
    def make_auth_cache_key(cls, prefix, email):
        return hashlib.sha256(f'{prefix}:{email}'.encode()).hexdigest()

    @classmethod
    def set_signup_data(cls, email, signup_data, user_type):
        key = cls.make_auth_cache_key(cls.SIGNUP_DATA_PREFIX, email)
        cache_value = {**signup_data, 'user_type': user_type}
        CacheManager.SetCache(key, cache_value, CacheTTL.MEDIUM)
        logger.info('signup_data_cached', extra={'email': email, 'user_type': user_type})
        return {'success': True}

    @classmethod
    def set_otp_in_cache(cls, email):
        otp = cls.generate_otp()
        key = cls.make_auth_cache_key(cls.CACHE_PREFIX, email)
        CacheManager.SetCache(key, cls.hash_otp(otp), CacheTTL.MEDIUM)

        send_otp_email_task.delay(email, otp)
        logger.info('otp_set', extra={'email': email, 'expires_in': CacheTTL.MEDIUM})
        return {'email': email, 'expires_in': CacheTTL.MEDIUM, 'message': 'OTP sent to email'}
    
    @classmethod
    def verify_otp(cls, email, input_otp):
        key = cls.make_auth_cache_key(cls.CACHE_PREFIX, email)
        cached = CacheManager.GetCache(key)

        if not cached['success']:
            return {'success': False, 'message': 'OTP expired or not found'}

        if cached['data'] == cls.hash_otp(input_otp):
            return {'success': True, 'message': 'OTP verified successfully'}

        return {'success': False, 'message': 'Invalid OTP'}






    # ---------------------------
    # 4. GET / INVALIDATE OTP
    # ---------------------------
    @classmethod
    def get_otp(cls, email):
        key = cls.make_auth_cache_key(cls.CACHE_PREFIX, email)
        cached = CacheManager.GetCache(key)
        return cached['data'] if cached['success'] else None

    @classmethod
    def invalidate_otp(cls, email):
        otp_key  = cls.make_auth_cache_key(cls.CACHE_PREFIX, email)
        data_key = cls.make_auth_cache_key(cls.SIGNUP_DATA_PREFIX, email)
        CacheManager.DeleteCache(otp_key)
        CacheManager.DeleteCache(data_key)

    # ---------------------------
    # 5. GET SIGNUP DATA
    # ---------------------------
    @classmethod
    def get_signup_data(cls, email):
        key = cls.make_auth_cache_key(cls.SIGNUP_DATA_PREFIX, email)
        cached = CacheManager.GetCache(key)
        return cached['data'] if cached['success'] else None

    # ---------------------------
    # 6. VERIFY OTP
    # ---------------------------
    











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
        

class LoginService:

    # ---------------------------
    # 1. LOGIN — returns JWT tokens
    # ---------------------------
    @staticmethod
    def login(email, password):
        user = authenticate(username=email, password=password)

        if user is None:
            logger.warning('login_failed_invalid_credentials', extra={'email': email})
            return {'status': False, 'message': 'Invalid email or password.'}

        if not user.is_active:
            logger.warning('login_failed_inactive_user', extra={'email': email})
            return {'status': False, 'message': 'Account is inactive.'}

        refresh = RefreshToken.for_user(user)
        logger.info('login_success', extra={'email': email, 'user_id': user.id, 'user_type': user.user_type})

        return {
            'status':        True,
            'access':        str(refresh.access_token),
            'refresh':       str(refresh),
            'user_type':     user.user_type,
            'user_id':       user.id,
        }


class LogoutService:

    # ---------------------------
    # 1. LOGOUT — blacklists refresh token
    # ---------------------------
    @staticmethod
    def logout(refresh_token: str):
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info('logout_success')
            return {'status': True, 'message': 'Logged out successfully.'}
        except Exception:
            logger.warning('logout_invalid_token', exc_info=True)
            return {'status': False, 'message': 'Invalid or expired token.'}


class PasswordResetService:

    RESET_OTP_PREFIX  = 'auth:reset_otp'
    RESET_EMAIL_PREFIX = 'auth:reset_email'

    # ---------------------------
    # 1. SEND RESET OTP
    # ---------------------------
    @classmethod
    def send_reset_otp(cls, email):
        if not User.objects.filter(email=email).exists():
            # Return success to avoid email enumeration
            logger.warning('password_reset_email_not_found', extra={'email': email})
            return {'status': True, 'message': 'If this email exists, an OTP has been sent.'}

        otp     = str(random.randint(100000, 999999))
        timeout = getattr(settings, 'OTP_TIMEOUT', 300)

        otp_key = hashlib.sha256(f'{cls.RESET_OTP_PREFIX}:{email}'.encode()).hexdigest()
        cache.set(otp_key, hashlib.sha256(otp.encode()).hexdigest(), timeout=timeout)

        send_password_reset_otp_task.delay(email, otp)
        logger.info('password_reset_otp_sent', extra={'email': email})
        return {'status': True, 'message': 'If this email exists, an OTP has been sent.'}

    # ---------------------------
    # 2. VERIFY OTP + SET NEW PASSWORD
    # ---------------------------
    @classmethod
    def verify_otp_and_reset(cls, email, otp_input, new_password):
        otp_key    = hashlib.sha256(f'{cls.RESET_OTP_PREFIX}:{email}'.encode()).hexdigest()
        cached_otp = cache.get(otp_key)

        if not cached_otp:
            logger.warning('password_reset_otp_expired', extra={'email': email})
            return {'status': False, 'message': 'OTP expired or not found.'}

        if cached_otp != hashlib.sha256(otp_input.encode()).hexdigest():
            logger.warning('password_reset_otp_invalid', extra={'email': email})
            return {'status': False, 'message': 'Invalid OTP.'}

        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save(update_fields=['password'])
            cache.delete(otp_key)
            logger.info('password_reset_success', extra={'email': email, 'user_id': user.id})
            return {'status': True, 'message': 'Password reset successfully.'}
        except User.DoesNotExist:
            logger.error('password_reset_user_not_found', extra={'email': email})
            return {'status': False, 'message': 'User not found.'}
        except Exception:
            logger.critical('password_reset_unexpected_error', extra={'email': email}, exc_info=True)
            return {'status': False, 'message': 'An unexpected error occurred.'}
