import logging
from core.enum import GenderChoices, RoleChoices
from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
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
    PasswordResetConfirmSerializer,
    PasswordChangeSerializer,
    LogoutSerializer,
)
from authentication.services import AuthEmailService, ProfileCreationService, LoginService, LogoutService, PasswordResetService, PasswordChangeService

logger = logging.getLogger(__name__)



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
    def _register(self, request, serializer_class):
        email     = request.data.get('email')
        user_type = request.data.get('user_type')
        serializer = serializer_class(data=request.data)

        logger.info(f'{email}_register_attempt', extra={'email': email})

        if not serializer.is_valid():
            logger.warning(f'{user_type}_register_validation_failed', extra={'email': email, 'errors': serializer.errors})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            AuthEmailService.set_register_otp_in_cache(email, serializer.to_cache(user_type))
            logger.info(f'{user_type}_register_otp_sent', extra={'email': email})
            return Response({'message': 'OTP sent to email. Verify to complete registration.'}, status=status.HTTP_200_OK)
        except Exception:
            logger.error(f'{user_type}_register_otp_send_failed', extra={'email': email}, exc_info=True)
            return Response({'error': 'Failed to send OTP.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






    # --------------------------------------------------
    # REGISTER ACTIONS — one per user type
    # --------------------------------------------------
    @swagger_auto_schema(
        tags=['Signup'], 
        operation_summary='Step 1 — Doctor: submit data & send OTP',
        request_body=None,
        consumes=['multipart/form-data'],
        manual_parameters=[
            openapi.Parameter('email', openapi.IN_FORM, description='Email address', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('password', openapi.IN_FORM, description='Password', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('password2', openapi.IN_FORM, description='Confirm password', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('user_type', openapi.IN_FORM, description='Selec user type', type=openapi.TYPE_STRING, enum=[choice[0] for choice in RoleChoices.choices],required=True),
            openapi.Parameter('first_name', openapi.IN_FORM, description='First name', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('middle_name', openapi.IN_FORM, description='Middle name', type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('last_name', openapi.IN_FORM, description='Last name', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('gender', openapi.IN_FORM, description='Select gender', type=openapi.TYPE_STRING, enum=[choice[0] for choice in GenderChoices.choices], required=True),
            openapi.Parameter('contact_number', openapi.IN_FORM, description='Contact number', type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('division', openapi.IN_FORM, description='Division ID', type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('district', openapi.IN_FORM, description='District ID', type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('upozila', openapi.IN_FORM, description='Upozila ID', type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('union', openapi.IN_FORM, description='Union ID', type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('license_number', openapi.IN_FORM, description='Medical license number', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('license_validity', openapi.IN_FORM, description='License validity date YYYY-MM-DD', type=openapi.TYPE_STRING, required=True),
        ],
        responses={200: 'OTP sent', 400: 'Validation error', 500: 'Server error'},
    )
    
    @action(detail=False, methods=['post'], url_path='doctor/register')
    def doctor_register(self, request):
        return self._register(request, DoctorSignUPSerializer)
        





   
    #-------------------------------------------------
    # Regular user registration
    #----------------------------------------------------
    @swagger_auto_schema(
        tags=['Signup'], 
        operation_summary='Step 1 — User: submit data & send OTP',
        request_body=None,
        consumes=['multipart/form-data'],
        manual_parameters=[
            openapi.Parameter('email', openapi.IN_FORM, description='Email address', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('password', openapi.IN_FORM, description='Password', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('password2', openapi.IN_FORM, description='Confirm password', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('first_name', openapi.IN_FORM, description='First name', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('last_name', openapi.IN_FORM, description='Last name', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('gender', openapi.IN_FORM, description='Select gender', type=openapi.TYPE_STRING, enum=[choice[0] for choice in GenderChoices.choices], required=True),
            openapi.Parameter('contact_number', openapi.IN_FORM, description='Contact number', type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('date_of_birth', openapi.IN_FORM, description='YYYY-MM-DD', type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('address', openapi.IN_FORM, description='Address', type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('division', openapi.IN_FORM, description='Division ID', type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('district', openapi.IN_FORM, description='District ID', type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('upozila', openapi.IN_FORM, description='Upozila ID', type=openapi.TYPE_INTEGER, required=True),
        ],
        responses={200: 'OTP sent', 400: 'Validation error', 500: 'Server error'},
    )
    @action(detail=False, methods=['post'], url_path='user/register')
    def user_register(self, request):
        return self._register(request, UserSignUpSerializer)




   




    #====================================== 
    @swagger_auto_schema(
        tags=['Signup'], operation_summary='Step 1 — Blood Donor: submit data & send OTP',
        request_body=None,
        consumes=['multipart/form-data'],
        manual_parameters=[
            openapi.Parameter('email', openapi.IN_FORM, description='Email address', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('password', openapi.IN_FORM, description='Password', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('password2', openapi.IN_FORM, description='Confirm password', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('first_name', openapi.IN_FORM, description='First name', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('last_name', openapi.IN_FORM, description='Last name', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('gender', openapi.IN_FORM, description='Select gender', type=openapi.TYPE_STRING, enum=[choice[0] for choice in GenderChoices.choices], required=True),
            openapi.Parameter('date_of_birth', openapi.IN_FORM, description='YYYY-MM-DD', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('contact_number', openapi.IN_FORM, description='Contact number', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('blood_group', openapi.IN_FORM, description='A+ / A- / B+ / B- / AB+ / AB- / O+ / O-', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('availability', openapi.IN_FORM, description='available / unavailable', type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('last_donated', openapi.IN_FORM, description='YYYY-MM-DD', type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('address', openapi.IN_FORM, description='Address', type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('division', openapi.IN_FORM, description='Division ID', type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('district', openapi.IN_FORM, description='District ID', type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('upozila', openapi.IN_FORM, description='Upozila ID', type=openapi.TYPE_INTEGER, required=True),
        ],
        responses={200: 'OTP sent', 400: 'Validation error', 500: 'Server error'},
    )
    @action(detail=False, methods=['post'], url_path='blood-donor/register')
    def blood_donor_register(self, request):
        return self._register(request, BloodDonorSignUpSerializer)










    #======================================= Ambulance=====================
    @swagger_auto_schema(
        tags=['Signup'], operation_summary='Step 1 — Ambulance: submit data & send OTP',
        request_body=None,
        consumes=['multipart/form-data'],
        manual_parameters=[
            openapi.Parameter('email', openapi.IN_FORM, description='Email address', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('password', openapi.IN_FORM, description='Password', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('password2', openapi.IN_FORM, description='Confirm password', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('owner_name', openapi.IN_FORM, description='Owner full name', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('contact_number', openapi.IN_FORM, description='Contact number', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('ambulance_type', openapi.IN_FORM, description='basic / advanced / icu', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('vehicle_number', openapi.IN_FORM, description='Vehicle registration number', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('address', openapi.IN_FORM, description='Address', type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('division', openapi.IN_FORM, description='Division ID', type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('district', openapi.IN_FORM, description='District ID', type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('upozila', openapi.IN_FORM, description='Upozila ID', type=openapi.TYPE_INTEGER, required=True),
        ],
        responses={200: 'OTP sent', 400: 'Validation error', 500: 'Server error'},
    )
    @action(detail=False, methods=['post'], url_path='ambulance/register')
    def ambulance_register(self, request):
        return self._register(request, AmbulanceSignUpSerializer)





    #-================================ Pharmacy========================
    @swagger_auto_schema(
        tags=['Signup'], operation_summary='Step 1 — Pharmacy: submit data & send OTP',
        request_body=None,
        consumes=['multipart/form-data'],
        manual_parameters=[
            openapi.Parameter('email', openapi.IN_FORM, description='Email address', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('password', openapi.IN_FORM, description='Password', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('password2', openapi.IN_FORM, description='Confirm password', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('pharmacy_name', openapi.IN_FORM, description='Pharmacy name', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('owner_name', openapi.IN_FORM, description='Owner full name', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('contact_number', openapi.IN_FORM, description='Contact number', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('license_number', openapi.IN_FORM, description='License number', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('license_validity', openapi.IN_FORM, description='YYYY-MM-DD', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('address', openapi.IN_FORM, description='Address', type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('division', openapi.IN_FORM, description='Division ID', type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('district', openapi.IN_FORM, description='District ID', type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('upozila', openapi.IN_FORM, description='Upozila ID', type=openapi.TYPE_INTEGER, required=True),
        ],
        responses={200: 'OTP sent', 400: 'Validation error', 500: 'Server error'},
    )
    @action(detail=False, methods=['post'], url_path='pharmacy/register')
    def pharmacy_register(self, request):
        return self._register(request, PharmacySignUpSerializer)




    
    #========================== Diagnostic========================
    @swagger_auto_schema(
        tags=['Signup'], operation_summary='Step 1 — Diagnostic: submit data & send OTP',
        request_body=None,
        consumes=['multipart/form-data'],
        manual_parameters=[
            openapi.Parameter('email', openapi.IN_FORM, description='Email address', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('password', openapi.IN_FORM, description='Password', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('password2', openapi.IN_FORM, description='Confirm password', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('diagnostic_name', openapi.IN_FORM, description='Diagnostic center name', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('owner_name', openapi.IN_FORM, description='Owner full name', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('contact_number', openapi.IN_FORM, description='Contact number', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('license_number', openapi.IN_FORM, description='License number', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('license_validity', openapi.IN_FORM, description='YYYY-MM-DD', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('address', openapi.IN_FORM, description='Address', type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('division', openapi.IN_FORM, description='Division ID', type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('district', openapi.IN_FORM, description='District ID', type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('upozila', openapi.IN_FORM, description='Upozila ID', type=openapi.TYPE_INTEGER, required=True),
        ],
        responses={200: 'OTP sent', 400: 'Validation error', 500: 'Server error'},
    )
    @action(detail=False, methods=['post'], url_path='diagnostic/register')
    def diagnostic_register(self, request):
        return self._register(request, DiagnosticSignUpSerializer)



























    # --------------------------------------------------
    # SINGLE VERIFY — detects user_type from cache
    # --------------------------------------------------
    @swagger_auto_schema(
        tags=['Verify OTP'],
        operation_summary='Step 2 — Verify OTP & create profile (all user types)',
        operation_description=(
            'Send email + OTP. The user_type is stored in cache during registration '
            'and used here to create the correct profile atomically.'
        ),
    request_body=None,
    manual_parameters=[
            openapi.Parameter('email', openapi.IN_FORM, description='Registered email address', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('otp', openapi.IN_FORM, description='6-digit OTP sent to email', type=openapi.TYPE_STRING, required=True),
        ],
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
            user = create_fn(signup_data)
            AuthEmailService.invalidate_otp(email)
            refresh = RefreshToken.for_user(user)
            logger.info('verify_signup_complete', extra={'email': email, 'user_type': user_type})
            return Response({
                'message':   self._SUCCESS_MESSAGES[user_type],
                'user_id':   user.id,
                'email':     user.email,
                'user_type': user.user_type,
                'access':    str(refresh.access_token),
                'refresh':   str(refresh),
            }, status=status.HTTP_201_CREATED)
        except DatabaseError:
            logger.error('verify_db_error', extra={'email': email, 'user_type': user_type}, exc_info=True)
            return Response({'error': 'Database error. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            logger.critical('verify_unexpected_error', extra={'email': email, 'user_type': user_type}, exc_info=True)
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)













    # --------------------------------------------------
    # RESEND OTP
    # --------------------------------------------------
    @swagger_auto_schema(
        tags=['Verify OTP'],
        operation_summary='Resend OTP — resend OTP to email',
        request_body=None,
        consumes=['multipart/form-data'],
        manual_parameters=[
            openapi.Parameter('email', openapi.IN_FORM, description='Registered email address', type=openapi.TYPE_STRING, required=True),
        ],
        responses={200: 'OTP resent', 400: 'No signup session found'},
    )
    @action(detail=False, methods=['post'], url_path='resend-otp')
    def resend_otp(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'email is required.'}, status=status.HTTP_400_BAD_REQUEST)
        result = AuthEmailService.resend_otp(email)
        if not result['status']:
            return Response({'error': result['message']}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': result['message']}, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class LoginViewSet(GenericViewSet):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Login Access Management'],
        operation_summary='Login — returns JWT access + refresh tokens',
        request_body=None,
        consumes=['multipart/form-data'],
        manual_parameters=[
            openapi.Parameter('email', openapi.IN_FORM, description='Email address', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('password', openapi.IN_FORM, description='Password', type=openapi.TYPE_STRING, required=True),
        ],
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
        tags=['Login Access Management'],
        operation_summary='Logout — blacklists the refresh token',
        request_body=None,
        consumes=['multipart/form-data'],
        manual_parameters=[
            openapi.Parameter('refresh', openapi.IN_FORM, description='Refresh token to blacklist', type=openapi.TYPE_STRING, required=True),
        ],
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

    # STEP 1 — send OTP
    @swagger_auto_schema(
        tags=['Password Management'],
        operation_summary='Step 1 — Send password reset OTP',
        request_body=None,
        consumes=['multipart/form-data'],
        manual_parameters=[
            openapi.Parameter('email', openapi.IN_FORM, description='Registered email address', type=openapi.TYPE_STRING, required=True),
        ],
        responses={200: 'OTP sent', 400: 'Validation error'},
    )
    @action(detail=False, methods=['post'], url_path='send-otp')
    def send_otp(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        result = PasswordResetService.send_reset_otp(serializer.validated_data['email'])
        return Response({'message': result['message']}, status=status.HTTP_200_OK)

    # STEP 2 — verify OTP, get reset token
    @swagger_auto_schema(
        tags=['Password Management'],
        operation_summary='Step 2 — Verify OTP, receive reset token',
        request_body=None,
        consumes=['multipart/form-data'],
        manual_parameters=[
            openapi.Parameter('email', openapi.IN_FORM, description='Registered email address', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('otp', openapi.IN_FORM, description='6-digit OTP sent to email', type=openapi.TYPE_STRING, required=True),
        ],
        responses={200: 'Reset token returned', 400: 'Invalid OTP'},
    )
    @action(detail=False, methods=['post'], url_path='verify-otp')
    def verify_otp(self, request):
        serializer = PasswordResetVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        result = PasswordResetService.verify_otp(
            email=serializer.validated_data['email'],
            otp_input=serializer.validated_data['otp'],
        )
        if not result['status']:
            return Response({'error': result['message']}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'reset_token': result['reset_token']}, status=status.HTTP_200_OK)

    # STEP 3 — reset password using token
    @swagger_auto_schema(
        tags=['Password Management'],
        operation_summary='Step 3 — Reset password using reset token',
        request_body=None,
        consumes=['multipart/form-data'],
        manual_parameters=[
            openapi.Parameter('email', openapi.IN_FORM, description='Registered email address', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('reset_token', openapi.IN_FORM, description='Token received from verify-otp step', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('new_password', openapi.IN_FORM, description='New password (min 9 chars)', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('new_password2', openapi.IN_FORM, description='Confirm new password', type=openapi.TYPE_STRING, required=True),
        ],
        responses={200: 'Password reset', 400: 'Invalid token or validation error'},
    )
    @action(detail=False, methods=['post'], url_path='reset-password')
    def reset_password(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        result = PasswordResetService.reset_password(
            email=serializer.validated_data['email'],
            reset_token=serializer.validated_data['reset_token'],
            new_password=serializer.validated_data['new_password'],
        )
        if not result['status']:
            return Response({'error': result['message']}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': result['message']}, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class PasswordChangeViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Password Management'],
        operation_summary='Change password — authenticated user',
        request_body=None,
        consumes=['multipart/form-data'],
        manual_parameters=[
            openapi.Parameter('current_password', openapi.IN_FORM, description='Current password', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('new_password', openapi.IN_FORM, description='New password (min 9 chars)', type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('new_password2', openapi.IN_FORM, description='Confirm new password', type=openapi.TYPE_STRING, required=True),
        ],
        responses={200: 'Password changed + new tokens', 400: 'Validation error', 401: 'Wrong current password'},
    )
    @action(detail=False, methods=['post'], url_path='change-password')
    def change_password(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        result = PasswordChangeService.change_password(
            user=request.user,
            current_password=serializer.validated_data['current_password'],
            new_password=serializer.validated_data['new_password'],
        )

        if not result['status']:
            return Response({'error': result['message']}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({
            'message': result['message'],
            'access':  result['access'],
            'refresh': result['refresh'],
        }, status=status.HTTP_200_OK)
