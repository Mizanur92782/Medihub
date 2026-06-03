import logging
from authentication.cache_keys import SignupCacheKeys
from authentication.models import User
from cache.manager import CacheManager
from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import DatabaseError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from authentication.serializer import (
    DoctorSignUPSerializer,
    UserSignUpSerializer,
    BloodDonorSignUpSerializer,
    AmbulanceSignUpSerializer,
    PharmacySignUpSerializer,
    DiagnosticSignUpSerializer,
    LoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetVerifySerializer,
    LogoutSerializer,
)
from authentication.services import AuthEmailService, ProfileCreationService, LoginService, LogoutService, PasswordResetService



''''logget to track log'''
logger = logging.getLogger(__name__)



def _form_params(*fields):
    """Build openapi form parameters from (name, type, required, description) tuples."""
    return [
        openapi.Parameter(
            name, openapi.IN_FORM,
            type=t,
            required=req,
            description=desc,
        )
        for name, t, req, desc in fields
    ]




_verify_params = _form_params(
    ('email', openapi.TYPE_STRING, True,  'Registered email address'),
    ('otp',   openapi.TYPE_STRING, True,  '6-digit OTP sent to email'),
)


@method_decorator(csrf_exempt, name='dispatch')
class SignupViewSet(GenericViewSet):
    permission_classes = [AllowAny]

    _PROFILE_CREATORS = {
        'doctor':      ProfileCreationService.create_doctor_profile,
        'user':        ProfileCreationService.create_user_profile,
        'blood_donor': ProfileCreationService.create_blood_donor_profile,
        'ambulance':   ProfileCreationService.create_ambulance_profile,
        'pharmacy':    ProfileCreationService.create_pharmacy_profile,
        'diagnostic':  ProfileCreationService.create_diagnostic_profile,
    }

    _SUCCESS_MESSAGES = {
        'doctor':      'Doctor registered successfully.',
        'user':        'User registered successfully.',
        'blood_donor': 'Blood donor registered successfully.',
        'ambulance':   'Ambulance registered successfully.',
        'pharmacy':    'Pharmacy registered successfully.',
        'diagnostic':  'Diagnostic center registered successfully.',
    }

    # --------------------------------------------------
    # SHARED REGISTER HELPER
    # --------------------------------------------------
    def _register(self, request, serializer_class, user_type):
        email      = request.data.get('email')
        serializer = serializer_class(data=request.data)

        logger.info(f'{email}_register_attempt', extra={'email': email})

        if not serializer.is_valid():
            logger.warning(f'{email}_register_validation_failed', extra={'email': email, 'errors': serializer.errors})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            logger.warning(f'{email}_register_email_exists', extra={'email': email})
            return Response({'email': 'Email is already registered.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            #set singup data in cache with OTP
           
            

            AuthEmailService.set_signup_data(email, serializer.validated_data, user_type)
            AuthEmailService.set_otp_in_cache(email)
            logger.info(f'{email}_register_otp_sent', extra={'email': email})
            return Response({'message': 'OTP sent to email. Verify to complete registration.'}, status=status.HTTP_200_OK)
        except Exception:
            logger.error(f'{email}_register_otp_send_failed', extra={'email': email}, exc_info=True)
        

            return Response({'error': 'Failed to send OTP.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    # --------------------------------------------------
    # SINGLE VERIFY — detects user_type from cache
    # --------------------------------------------------
    @swagger_auto_schema(
        tags=['Signup'],
        operation_summary='Step 2 — Verify OTP & create profile (all user types)',
        operation_description=(
            'Send email + OTP. The user_type is stored in cache during registration '
            'and used here to create the correct profile atomically.'
        ),
        manual_parameters=_verify_params,
        consumes=['multipart/form-data'],
        responses={201: 'Registered', 400: 'Invalid OTP / session expired', 500: 'Server error'},
    )

    
    @action(detail=False, methods=['post'], url_path='verify')
    def verify(self, request):
        email     = request.data.get('email')
        otp_input = request.data.get('otp')

        logger.info('verify_attempt', extra={'email': email})

        if not email or not otp_input:
            return Response({'error': 'email and otp are required.'}, status=status.HTTP_400_BAD_REQUEST)

        otp_result = AuthEmailService.verify_otp(email, otp_input)
        if not otp_result['success']:
            logger.warning('verify_otp_failed', extra={'email': email, 'reason': otp_result['message']})
            return Response({'otp': otp_result['message']}, status=status.HTTP_400_BAD_REQUEST)

        signup_data = AuthEmailService.get_signup_data(email)
        if not signup_data:
            logger.warning('verify_cache_miss', extra={'email': email})
            return Response({'error': 'Signup session expired. Please register again.'}, status=status.HTTP_400_BAD_REQUEST)

        user_type = signup_data.pop('user_type', None)
        create_fn = self._PROFILE_CREATORS.get(user_type)
        if not create_fn:
            logger.error('verify_unknown_user_type', extra={'email': email, 'user_type': user_type})
            return Response({'error': 'Invalid signup session.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            create_fn(signup_data)
            AuthEmailService.invalidate_otp(email)
            logger.info('verify_signup_complete', extra={'email': email, 'user_type': user_type})
            return Response({'message': self._SUCCESS_MESSAGES[user_type]}, status=status.HTTP_201_CREATED)
        except DatabaseError:
            logger.error('verify_db_error', extra={'email': email, 'user_type': user_type}, exc_info=True)
            return Response({'error': 'Database error. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            logger.critical('verify_unexpected_error', extra={'email': email, 'user_type': user_type}, exc_info=True)
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # --------------------------------------------------
    # REGISTER ACTIONS — one per user type
    # --------------------------------------------------
    @swagger_auto_schema(
        tags=['Doctor Signup'], operation_summary='Step 1 — Doctor: submit data & send OTP',
        consumes=['multipart/form-data'],
        manual_parameters=_form_params(
            ('email',          openapi.TYPE_STRING, True,  'Email address'),
            ('password',       openapi.TYPE_STRING, True,  'Password'),
            ('password2',      openapi.TYPE_STRING, True,  'Confirm password'),
            ('first_name',     openapi.TYPE_STRING, True,  'First name'),
            ('middle_name',    openapi.TYPE_STRING, False, 'Middle name'),
            ('last_name',      openapi.TYPE_STRING, True,  'Last name'),
            ('gender',         openapi.TYPE_STRING, True,  'male / female / other'),
            ('contact_number', openapi.TYPE_STRING, True,  'Contact number'),
            ('division',       openapi.TYPE_INTEGER, True, 'Division ID'),
            ('district',       openapi.TYPE_INTEGER, True, 'District ID'),
            ('upozila',        openapi.TYPE_INTEGER, True, 'Upozila ID'),
            ('union',          openapi.TYPE_INTEGER, True, 'Union ID'),
        ),
        responses={200: 'OTP sent', 400: 'Validation error', 500: 'Server error'},
    )
    @action(detail=False, methods=['post'], url_path='doctor/register')
    def doctor_register(self, request):
        return self._register(request, DoctorSignUPSerializer, 'doctor')

    @swagger_auto_schema(
        tags=['User Signup'], operation_summary='Step 1 — User: submit data & send OTP',
        consumes=['multipart/form-data'],
        manual_parameters=_form_params(
            ('email',          openapi.TYPE_STRING,  True,  'Email address'),
            ('password',       openapi.TYPE_STRING,  True,  'Password'),
            ('password2',      openapi.TYPE_STRING,  True,  'Confirm password'),
            ('first_name',     openapi.TYPE_STRING,  True,  'First name'),
            ('last_name',      openapi.TYPE_STRING,  True,  'Last name'),
            ('gender',         openapi.TYPE_STRING,  True,  'male / female / other'),
            ('contact_number', openapi.TYPE_STRING,  False, 'Contact number'),
            ('date_of_birth',  openapi.TYPE_STRING,  False, 'YYYY-MM-DD'),
            ('address',        openapi.TYPE_STRING,  False, 'Address'),
            ('division',       openapi.TYPE_INTEGER, True,  'Division ID'),
            ('district',       openapi.TYPE_INTEGER, True,  'District ID'),
            ('upozila',        openapi.TYPE_INTEGER, True,  'Upozila ID'),
        ),
        responses={200: 'OTP sent', 400: 'Validation error', 500: 'Server error'},
    )
    @action(detail=False, methods=['post'], url_path='user/register')
    def user_register(self, request):
        return self._register(request, UserSignUpSerializer, 'user')

    @swagger_auto_schema(
        tags=['Blood Donor Signup'], operation_summary='Step 1 — Blood Donor: submit data & send OTP',
        consumes=['multipart/form-data'],
        manual_parameters=_form_params(
            ('email',          openapi.TYPE_STRING,  True,  'Email address'),
            ('password',       openapi.TYPE_STRING,  True,  'Password'),
            ('password2',      openapi.TYPE_STRING,  True,  'Confirm password'),
            ('first_name',     openapi.TYPE_STRING,  True,  'First name'),
            ('last_name',      openapi.TYPE_STRING,  True,  'Last name'),
            ('gender',         openapi.TYPE_STRING,  True,  'male / female / other'),
            ('date_of_birth',  openapi.TYPE_STRING,  True,  'YYYY-MM-DD'),
            ('contact_number', openapi.TYPE_STRING,  True,  'Contact number'),
            ('blood_group',    openapi.TYPE_STRING,  True,  'A+ / A- / B+ / B- / AB+ / AB- / O+ / O-'),
            ('availability',   openapi.TYPE_STRING,  False, 'available / unavailable'),
            ('last_donated',   openapi.TYPE_STRING,  False, 'YYYY-MM-DD'),
            ('address',        openapi.TYPE_STRING,  False, 'Address'),
            ('division',       openapi.TYPE_INTEGER, True,  'Division ID'),
            ('district',       openapi.TYPE_INTEGER, True,  'District ID'),
            ('upozila',        openapi.TYPE_INTEGER, True,  'Upozila ID'),
        ),
        responses={200: 'OTP sent', 400: 'Validation error', 500: 'Server error'},
    )
    @action(detail=False, methods=['post'], url_path='blood-donor/register')
    def blood_donor_register(self, request):
        return self._register(request, BloodDonorSignUpSerializer, 'blood_donor')

    @swagger_auto_schema(
        tags=['Ambulance Signup'], operation_summary='Step 1 — Ambulance: submit data & send OTP',
        consumes=['multipart/form-data'],
        manual_parameters=_form_params(
            ('email',          openapi.TYPE_STRING,  True,  'Email address'),
            ('password',       openapi.TYPE_STRING,  True,  'Password'),
            ('password2',      openapi.TYPE_STRING,  True,  'Confirm password'),
            ('owner_name',     openapi.TYPE_STRING,  True,  'Owner full name'),
            ('contact_number', openapi.TYPE_STRING,  True,  'Contact number'),
            ('ambulance_type', openapi.TYPE_STRING,  True,  'basic / advanced / icu'),
            ('vehicle_number', openapi.TYPE_STRING,  True,  'Vehicle registration number'),
            ('address',        openapi.TYPE_STRING,  False, 'Address'),
            ('division',       openapi.TYPE_INTEGER, True,  'Division ID'),
            ('district',       openapi.TYPE_INTEGER, True,  'District ID'),
            ('upozila',        openapi.TYPE_INTEGER, True,  'Upozila ID'),
        ),
        responses={200: 'OTP sent', 400: 'Validation error', 500: 'Server error'},
    )
    @action(detail=False, methods=['post'], url_path='ambulance/register')
    def ambulance_register(self, request):
        return self._register(request, AmbulanceSignUpSerializer, 'ambulance')

    @swagger_auto_schema(
        tags=['Pharmacy Signup'], operation_summary='Step 1 — Pharmacy: submit data & send OTP',
        consumes=['multipart/form-data'],
        manual_parameters=_form_params(
            ('email',            openapi.TYPE_STRING,  True,  'Email address'),
            ('password',         openapi.TYPE_STRING,  True,  'Password'),
            ('password2',        openapi.TYPE_STRING,  True,  'Confirm password'),
            ('pharmacy_name',    openapi.TYPE_STRING,  True,  'Pharmacy name'),
            ('owner_name',       openapi.TYPE_STRING,  True,  'Owner full name'),
            ('contact_number',   openapi.TYPE_STRING,  True,  'Contact number'),
            ('license_number',   openapi.TYPE_STRING,  True,  'License number'),
            ('license_validity', openapi.TYPE_STRING,  True,  'YYYY-MM-DD'),
            ('address',          openapi.TYPE_STRING,  False, 'Address'),
            ('division',         openapi.TYPE_INTEGER, True,  'Division ID'),
            ('district',         openapi.TYPE_INTEGER, True,  'District ID'),
            ('upozila',          openapi.TYPE_INTEGER, True,  'Upozila ID'),
        ),
        responses={200: 'OTP sent', 400: 'Validation error', 500: 'Server error'},
    )
    @action(detail=False, methods=['post'], url_path='pharmacy/register')
    def pharmacy_register(self, request):
        return self._register(request, PharmacySignUpSerializer, 'pharmacy')

    @swagger_auto_schema(
        tags=['Diagnostic Signup'], operation_summary='Step 1 — Diagnostic: submit data & send OTP',
        consumes=['multipart/form-data'],
        manual_parameters=_form_params(
            ('email',            openapi.TYPE_STRING,  True,  'Email address'),
            ('password',         openapi.TYPE_STRING,  True,  'Password'),
            ('password2',        openapi.TYPE_STRING,  True,  'Confirm password'),
            ('diagnostic_name',  openapi.TYPE_STRING,  True,  'Diagnostic center name'),
            ('owner_name',       openapi.TYPE_STRING,  True,  'Owner full name'),
            ('contact_number',   openapi.TYPE_STRING,  True,  'Contact number'),
            ('license_number',   openapi.TYPE_STRING,  True,  'License number'),
            ('license_validity', openapi.TYPE_STRING,  True,  'YYYY-MM-DD'),
            ('address',          openapi.TYPE_STRING,  False, 'Address'),
            ('division',         openapi.TYPE_INTEGER, True,  'Division ID'),
            ('district',         openapi.TYPE_INTEGER, True,  'District ID'),
            ('upozila',          openapi.TYPE_INTEGER, True,  'Upozila ID'),
        ),
        responses={200: 'OTP sent', 400: 'Validation error', 500: 'Server error'},
    )
    @action(detail=False, methods=['post'], url_path='diagnostic/register')
    def diagnostic_register(self, request):
        return self._register(request, DiagnosticSignUpSerializer, 'diagnostic')


_email_params = _form_params(
    ('email', openapi.TYPE_STRING, True, 'Registered email address'),
)

_reset_verify_params = _form_params(
    ('email',         openapi.TYPE_STRING, True,  'Registered email address'),
    ('otp',           openapi.TYPE_STRING, True,  '6-digit OTP sent to email'),
    ('new_password',  openapi.TYPE_STRING, True,  'New password (min 9 chars)'),
    ('new_password2', openapi.TYPE_STRING, True,  'Confirm new password'),
)


@method_decorator(csrf_exempt, name='dispatch')
class LoginViewSet(GenericViewSet):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Auth'],
        operation_summary='Login — returns JWT access + refresh tokens',
        consumes=['multipart/form-data'],
        manual_parameters=_form_params(
            ('email',    openapi.TYPE_STRING, True, 'Email address'),
            ('password', openapi.TYPE_STRING, True, 'Password'),
        ),
        responses={200: 'Tokens returned', 400: 'Validation error', 401: 'Invalid credentials'},
    )
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        result = LoginService.login(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
        )

        if not result['status']:
            return Response({'error': result['message']}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(result, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Auth'],
        operation_summary='Logout — blacklists the refresh token',
        consumes=['multipart/form-data'],
        manual_parameters=_form_params(
            ('refresh', openapi.TYPE_STRING, True, 'Refresh token to blacklist'),
        ),
        responses={200: 'Logged out', 400: 'Invalid token'},
    )
    @action(detail=False, methods=['post'], url_path='logout')
    def logout(self, request):
        serializer = LogoutSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        result = LogoutService.logout(serializer.validated_data['refresh'])

        if not result['status']:
            return Response({'error': result['message']}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': result['message']}, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class PasswordResetViewSet(GenericViewSet):
    permission_classes = [AllowAny]

    # --------------------------------------------------
    # STEP 1 — send OTP to email
    # --------------------------------------------------
    @swagger_auto_schema(
        tags=['Password Reset'],
        operation_summary='Step 1 — Send password reset OTP',
        consumes=['multipart/form-data'],
        manual_parameters=_email_params,
        responses={200: 'OTP sent', 400: 'Validation error'},
    )
    @action(detail=False, methods=['post'], url_path='send-otp')
    def send_otp(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        result = PasswordResetService.send_reset_otp(serializer.validated_data['email'])
        return Response({'message': result['message']}, status=status.HTTP_200_OK)

    # --------------------------------------------------
    # STEP 2 — verify OTP + set new password
    # --------------------------------------------------
    @swagger_auto_schema(
        tags=['Password Reset'],
        operation_summary='Step 2 — Verify OTP and set new password',
        consumes=['multipart/form-data'],
        manual_parameters=_reset_verify_params,
        responses={200: 'Password reset', 400: 'Invalid OTP or validation error'},
    )
    @action(detail=False, methods=['post'], url_path='verify-otp')
    def verify_otp(self, request):
        serializer = PasswordResetVerifySerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        result = PasswordResetService.verify_otp_and_reset(
            email=serializer.validated_data['email'],
            otp_input=serializer.validated_data['otp'],
            new_password=serializer.validated_data['new_password'],
        )

        if not result['status']:
            return Response({'error': result['message']}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': result['message']}, status=status.HTTP_200_OK)
