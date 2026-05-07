import logging
from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import DatabaseError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from authentication.serializer import DoctorSignUPSerializer
from authentication.services import AuthEmailService, ProfileCreationService

logger = logging.getLogger(__name__)

_verify_body = openapi.Schema(
  type=openapi.TYPE_OBJECT,
  required=['email', 'otp'],
  properties={
    'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', example='doctor@example.com'),
    'otp':   openapi.Schema(type=openapi.TYPE_STRING, example='123456', description='6-digit OTP sent to email'),
  },
)


class SignupViewSet(GenericViewSet):
  permission_classes = [AllowAny]

  # --------------------------------------------------
  # STEP 1 — POST /api/auth/signup/doctor/register/
  # --------------------------------------------------
  @swagger_auto_schema(
    tags=['Doctor Signup'],
    operation_id='doctor_register',
    operation_summary='Step 1 — Submit signup data & receive OTP',
    operation_description=(
      'Validates all doctor signup fields, caches the data, '
      'and sends a 6-digit OTP to the provided email. '
      'Submit the OTP to `/doctor/verify/` to complete registration.'
    ),
    request_body=DoctorSignUPSerializer,
    responses={
      200: openapi.Response('OTP sent to email'),
      400: openapi.Response('Validation error'),
      500: openapi.Response('Server error'),
    },
  )
  @action(detail=False, methods=['post'], url_path='doctor/register')
  def doctor_register(self, request):
    serializer = DoctorSignUPSerializer(data=request.data)
    email = request.data.get('email')

    logger.info('doctor_register_attempt', extra={'email': email})

    if not serializer.is_valid():
      logger.warning('doctor_register_validation_failed', extra={
        'email': email,
        'errors': serializer.errors,
      })
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
      cache_data = serializer.to_cache()
      AuthEmailService.set_otp(email, cache_data)
      logger.info('doctor_register_otp_sent', extra={'email': email})
      return Response(
        {'message': 'OTP sent to email. Verify to complete registration.'},
        status=status.HTTP_200_OK,
      )

    except Exception:
      logger.error('doctor_register_otp_send_failed', extra={'email': email}, exc_info=True)
      return Response({'error': 'Failed to send OTP.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  # --------------------------------------------------
  # STEP 2 — POST /api/auth/signup/doctor/verify/
  # --------------------------------------------------
  @swagger_auto_schema(
    tags=['Doctor Signup'],
    operation_id='doctor_verify',
    operation_summary='Step 2 — Verify OTP & create doctor profile',
    operation_description=(
      'Verifies the OTP sent to the email. '
      'On success, loads cached signup data and creates the User + Doctor profile atomically.'
    ),
    request_body=_verify_body,
    responses={
      201: openapi.Response('Doctor registered successfully'),
      400: openapi.Response('Invalid/expired OTP or session expired'),
      500: openapi.Response('Server error'),
    },
  )
  @action(detail=False, methods=['post'], url_path='doctor/verify')
  def doctor_verify(self, request):
    email     = request.data.get('email')
    otp_input = request.data.get('otp')

    logger.info('doctor_verify_attempt', extra={'email': email})

    if not email or not otp_input:
      return Response({'error': 'email and otp are required.'}, status=status.HTTP_400_BAD_REQUEST)

    # 1. Verify OTP
    otp_result = AuthEmailService.verify_otp(email, otp_input)
    if not otp_result['status']:
      logger.warning('doctor_verify_otp_failed', extra={
        'email': email,
        'reason': otp_result['message'],
      })
      return Response({'otp': otp_result['message']}, status=status.HTTP_400_BAD_REQUEST)

    # 2. Load signup data from cache
    signup_data = AuthEmailService.get_signup_data(email)
    if not signup_data:
      logger.warning('doctor_verify_cache_miss', extra={'email': email})
      return Response(
        {'error': 'Signup session expired. Please register again.'},
        status=status.HTTP_400_BAD_REQUEST,
      )

    # 3. Create profile atomically — invalidate cache after success
    try:
      ProfileCreationService.create_doctor_profile(signup_data)
      AuthEmailService.invalidate_otp(email)
      logger.info('doctor_verify_signup_complete', extra={'email': email})
      return Response({'message': 'Doctor registered successfully.'}, status=status.HTTP_201_CREATED)

    except DatabaseError:
      logger.error('doctor_verify_db_error', extra={'email': email}, exc_info=True)
      return Response({'error': 'Database error. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception:
      logger.critical('doctor_verify_unexpected_error', extra={'email': email}, exc_info=True)
      return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
