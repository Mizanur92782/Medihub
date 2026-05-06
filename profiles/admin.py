from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from profiles.models.user_mod import User
from profiles.models.user_prof_mod import UserProfile
from profiles.models.doctor_prof_mod import (
    Specialization,
    SubSpecialization,
    Qualification,
    Hospital,
    Doctor,
    DoctorDetails,
    DoctorEducation,
    DoctorWorkingExperience,
    DoctorScheduling,
    DoctorRating,
)
from profiles.models.ambulance_prof_mod import AmbulanceProfile
from profiles.models.pharmacy_prof_mod import PharmacyProfile
from profiles.models.diagnostic_prof_mod import DiagnosticProfile
from profiles.models.blood_donor_mod import BloodDonor


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['id', 'email', 'role', 'is_blood_donor', 'is_active', 'is_staff', 'is_superuser', 'created']
    ordering = ['email']
    search_fields = ['email']
    list_filter = ['role', 'is_blood_donor', 'is_active', 'is_staff', 'is_superuser']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Role', {'fields': ('role', 'is_blood_donor')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'password1', 'password2', 'role')}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'first_name', 'last_name', 'gender', 'contact_number', 'district']
    search_fields = ['first_name', 'last_name', 'user__email']
    list_filter = ['gender', 'division', 'district']
    ordering = ['first_name']


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_eng', 'name_bn']
    search_fields = ['name_eng', 'name_bn']
    ordering = ['name_eng']


@admin.register(SubSpecialization)
class SubSpecializationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_eng', 'name_bn', 'specialization']
    search_fields = ['name_eng', 'name_bn']
    list_filter = ['specialization']
    ordering = ['name_eng']


@admin.register(Qualification)
class QualificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_eng', 'name_bn']
    search_fields = ['name_eng', 'name_bn']
    ordering = ['name_eng']


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_eng', 'name_bn']
    search_fields = ['name_eng', 'name_bn']
    ordering = ['name_eng']


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'specialization', 'license_number', 'license_validity', 'district']
    search_fields = ['first_name', 'last_name', 'license_number', 'user__email']
    list_filter = ['specialization', 'qualifications', 'hospital_affiliations', 'gender', 'division', 'district']
    filter_horizontal = ['qualifications', 'hospital_affiliations']
    ordering = ['first_name']


@admin.register(DoctorDetails)
class DoctorDetailsAdmin(admin.ModelAdmin):
    list_display = ['id', 'doctor', 'website', 'language']
    search_fields = ['doctor__first_name', 'doctor__last_name']


@admin.register(DoctorEducation)
class DoctorEducationAdmin(admin.ModelAdmin):
    list_display = ['id', 'doctor', 'institution', 'degree', 'start_at', 'end_at']
    search_fields = ['doctor__first_name', 'institution', 'degree']
    list_filter = ['degree']


@admin.register(DoctorWorkingExperience)
class DoctorWorkingExperienceAdmin(admin.ModelAdmin):
    list_display = ['id', 'doctor', 'institution', 'position', 'starting_at', 'end_at']
    search_fields = ['doctor__first_name', 'institution', 'position']


@admin.register(DoctorScheduling)
class DoctorSchedulingAdmin(admin.ModelAdmin):
    list_display = ['id', 'doctor', 'day', 'start', 'end']
    search_fields = ['doctor__first_name', 'doctor__last_name']
    list_filter = ['day']


@admin.register(DoctorRating)
class DoctorRatingAdmin(admin.ModelAdmin):
    list_display = ['id', 'doctor', 'user', 'rating', 'created']
    search_fields = ['doctor__first_name', 'user__email']
    list_filter = ['rating']
    ordering = ['-created']


@admin.register(AmbulanceProfile)
class AmbulanceProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner_name', 'vehicle_number', 'ambulance_type', 'is_available', 'district']
    search_fields = ['owner_name', 'vehicle_number', 'user__email']
    list_filter = ['ambulance_type', 'is_available', 'division', 'district']
    ordering = ['owner_name']


@admin.register(PharmacyProfile)
class PharmacyProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'pharmacy_name', 'owner_name', 'license_number', 'license_validity', 'is_open', 'district']
    search_fields = ['pharmacy_name', 'owner_name', 'license_number', 'user__email']
    list_filter = ['is_open', 'division', 'district']
    ordering = ['pharmacy_name']


@admin.register(DiagnosticProfile)
class DiagnosticProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'diagnostic_name', 'owner_name', 'license_number', 'license_validity', 'is_open', 'district']
    search_fields = ['diagnostic_name', 'owner_name', 'license_number', 'user__email']
    list_filter = ['is_open', 'division', 'district']
    ordering = ['diagnostic_name']


@admin.register(BloodDonor)
class BloodDonorAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'blood_group', 'availability', 'last_donated', 'district']
    search_fields = ['first_name', 'last_name', 'user__email']
    list_filter = ['blood_group', 'availability', 'gender', 'division', 'district']
    ordering = ['first_name']
