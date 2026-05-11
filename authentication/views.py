import logging
from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
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
)
from authentication.services import AuthEmailService, ProfileCreationService

logger = logging.getLogger(__name__)

_verify_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email', 'otp'],
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
        'otp':   openapi.Schema(type=openapi.TYPE_STRING, description='6-digit OTP'),
    },
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
    def _register(self, request, serializer_class, user_type: str):
        email      = request.data.get('email')
        serializer = serializer_class(data=request.data)

        logger.info(f'{user_type}_register_attempt', extra={'email': email})

        if not serializer.is_valid():
            logger.warning(f'{user_type}_register_validation_failed', extra={'email': email, 'errors': serializer.errors})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            AuthEmailService.set_otp(email, serializer.to_cache(user_type))
            logger.info(f'{user_type}_register_otp_sent', extra={'email': email})
            return Response({'message': 'OTP sent to email. Verify to complete registration.'}, status=status.HTTP_200_OK)
        except Exception:
            logger.error(f'{user_type}_register_otp_send_failed', extra={'email': email}, exc_info=True)
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
        request_body=_verify_body,
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
        if not otp_result['status']:
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
    @swagger_auto_schema(tags=['Doctor Signup'], operation_summary='Step 1 — Doctor: submit data & send OTP', request_body=DoctorSignUPSerializer, responses={200: 'OTP sent', 400: 'Validation error', 500: 'Server error'})
    @action(detail=False, methods=['post'], url_path='doctor/register')
    def doctor_register(self, request):
        return self._register(request, DoctorSignUPSerializer, 'doctor')

    @swagger_auto_schema(tags=['User Signup'], operation_summary='Step 1 — User: submit data & send OTP', request_body=UserSignUpSerializer, responses={200: 'OTP sent', 400: 'Validation error', 500: 'Server error'})
    @action(detail=False, methods=['post'], url_path='user/register')
    def user_register(self, request):
        return self._register(request, UserSignUpSerializer, 'user')

    @swagger_auto_schema(tags=['Blood Donor Signup'], operation_summary='Step 1 — Blood Donor: submit data & send OTP', request_body=BloodDonorSignUpSerializer, responses={200: 'OTP sent', 400: 'Validation error', 500: 'Server error'})
    @action(detail=False, methods=['post'], url_path='blood-donor/register')
    def blood_donor_register(self, request):
        return self._register(request, BloodDonorSignUpSerializer, 'blood_donor')

    @swagger_auto_schema(tags=['Ambulance Signup'], operation_summary='Step 1 — Ambulance: submit data & send OTP', request_body=AmbulanceSignUpSerializer, responses={200: 'OTP sent', 400: 'Validation error', 500: 'Server error'})
    @action(detail=False, methods=['post'], url_path='ambulance/register')
    def ambulance_register(self, request):
        return self._register(request, AmbulanceSignUpSerializer, 'ambulance')

    @swagger_auto_schema(tags=['Pharmacy Signup'], operation_summary='Step 1 — Pharmacy: submit data & send OTP', request_body=PharmacySignUpSerializer, responses={200: 'OTP sent', 400: 'Validation error', 500: 'Server error'})
    @action(detail=False, methods=['post'], url_path='pharmacy/register')
    def pharmacy_register(self, request):
        return self._register(request, PharmacySignUpSerializer, 'pharmacy')

    @swagger_auto_schema(tags=['Diagnostic Signup'], operation_summary='Step 1 — Diagnostic: submit data & send OTP', request_body=DiagnosticSignUpSerializer, responses={200: 'OTP sent', 400: 'Validation error', 500: 'Server error'})
    @action(detail=False, methods=['post'], url_path='diagnostic/register')
    def diagnostic_register(self, request):
        return self._register(request, DiagnosticSignUpSerializer, 'diagnostic')
