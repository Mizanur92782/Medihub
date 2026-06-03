from rest_framework import serializers
from core.enum import GenderChoices, BloodGroupChoices, AvailabilityChoices, AmbulanceTypeChoices, RoleChoices
from authentication.models import User
from location.models import Division, District, Upozila, Union


# --------------------------------------------------
# SHARED BASE — common fields + location cascade
# --------------------------------------------------
class _BaseSignUpSerializer(serializers.Serializer):

    email     = serializers.EmailField()
    password  = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=RoleChoices)

    division = serializers.PrimaryKeyRelatedField(queryset=Division.objects.all(), required=False, allow_null=True)
    district = serializers.PrimaryKeyRelatedField(queryset=District.objects.none(), required=False, allow_null=True)
    upozila  = serializers.PrimaryKeyRelatedField(queryset=Upozila.objects.none(), required=False, allow_null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        data = kwargs.get('data', {})

        division_id = data.get('division')
        if division_id:
            self.fields['district'].queryset = District.objects.filter(division_id=division_id)

        district_id = data.get('district')
        if district_id:
            self.fields['upozila'].queryset = Upozila.objects.filter(district_id=district_id)

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'Email already in use.'})
        return data

    def to_cache(self, user_type: str) -> dict:
        data = self.validated_data.copy()
        for field in ('division', 'district', 'upozila', 'union'):
            if data.get(field):
                data[field] = data[field].id
        data['user_type'] = user_type
        return data


# --------------------------------------------------
# DOCTOR
# --------------------------------------------------
class DoctorSignUPSerializer(_BaseSignUpSerializer):

    first_name     = serializers.CharField(max_length=100)
    middle_name    = serializers.CharField(max_length=100, required=False, allow_blank=True)
    last_name      = serializers.CharField(max_length=100)
    gender         = serializers.ChoiceField(choices=GenderChoices.choices)
    contact_number   = serializers.CharField(max_length=15, required=False, allow_blank=True)
    union            = serializers.PrimaryKeyRelatedField(queryset=Union.objects.none(), required=False, allow_null=True)
    license_number   = serializers.CharField(max_length=100)
    license_validity = serializers.DateField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        data = kwargs.get('data', {})
        upozila_id = data.get('upozila')
        if upozila_id:
            self.fields['union'].queryset = Union.objects.filter(upozila_id=upozila_id)


# --------------------------------------------------
# REGULAR USER
# --------------------------------------------------
class UserSignUpSerializer(_BaseSignUpSerializer):

    first_name     = serializers.CharField(max_length=100)
    last_name      = serializers.CharField(max_length=100)
    gender         = serializers.ChoiceField(choices=GenderChoices.choices)
    contact_number = serializers.CharField(max_length=15, required=False, allow_blank=True)
    date_of_birth  = serializers.DateField(required=False)
    address        = serializers.CharField(required=False, allow_blank=True)


# --------------------------------------------------
# BLOOD DONOR
# --------------------------------------------------
class BloodDonorSignUpSerializer(_BaseSignUpSerializer):

    first_name     = serializers.CharField(max_length=100)
    last_name      = serializers.CharField(max_length=100)
    gender         = serializers.ChoiceField(choices=GenderChoices.choices)
    date_of_birth  = serializers.DateField()
    contact_number = serializers.CharField(max_length=15)
    blood_group    = serializers.ChoiceField(choices=BloodGroupChoices.choices)
    availability   = serializers.ChoiceField(choices=AvailabilityChoices.choices, required=False)
    last_donated   = serializers.DateField(required=False)
    address        = serializers.CharField(required=False, allow_blank=True)


# --------------------------------------------------
# AMBULANCE
# --------------------------------------------------
class AmbulanceSignUpSerializer(_BaseSignUpSerializer):

    owner_name      = serializers.CharField(max_length=200)
    contact_number  = serializers.CharField(max_length=15)
    ambulance_type  = serializers.ChoiceField(choices=AmbulanceTypeChoices.choices)
    vehicle_number  = serializers.CharField(max_length=50)
    address         = serializers.CharField(required=False, allow_blank=True)


# --------------------------------------------------
# PHARMACY
# --------------------------------------------------
class PharmacySignUpSerializer(_BaseSignUpSerializer):

    pharmacy_name    = serializers.CharField(max_length=200)
    owner_name       = serializers.CharField(max_length=200)
    contact_number   = serializers.CharField(max_length=15)
    license_number   = serializers.CharField(max_length=100)
    license_validity = serializers.DateField()
    address          = serializers.CharField(required=False, allow_blank=True)


# --------------------------------------------------
# DIAGNOSTIC
# --------------------------------------------------
class DiagnosticSignUpSerializer(_BaseSignUpSerializer):

    diagnostic_name  = serializers.CharField(max_length=200)
    owner_name       = serializers.CharField(max_length=200)
    contact_number   = serializers.CharField(max_length=15)
    license_number   = serializers.CharField(max_length=100)
    license_validity = serializers.DateField()
    address          = serializers.CharField(required=False, allow_blank=True)


# --------------------------------------------------
# LOGIN
# --------------------------------------------------
class LoginSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True)


# --------------------------------------------------
# PASSWORD RESET — step 1: request OTP
# --------------------------------------------------
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


# --------------------------------------------------
# PASSWORD RESET — step 2: verify OTP
# --------------------------------------------------
class PasswordResetVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp   = serializers.CharField(max_length=6)


# --------------------------------------------------
# PASSWORD RESET — step 3: reset password with token
# --------------------------------------------------
class PasswordResetConfirmSerializer(serializers.Serializer):
    email        = serializers.EmailField()
    reset_token  = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=9)
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({'new_password': 'Passwords do not match.'})
        return data


# --------------------------------------------------
# PASSWORD CHANGE — authenticated user
# --------------------------------------------------
class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password     = serializers.CharField(write_only=True, min_length=9)
    new_password2    = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({'new_password': 'Passwords do not match.'})
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
