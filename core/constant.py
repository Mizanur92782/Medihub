from core.enum import RoleChoices
from profiles.models.ambulance_prof_mod import AmbulanceProfile
from profiles.models.blood_donor_mod import BloodDonor
from profiles.models.diagnostic_prof_mod import DiagnosticProfile
from profiles.models.doctor_prof_mod import Doctor
from profiles.models.pharmacy_prof_mod import PharmacyProfile
from profiles.models.user_prof_mod import RegularUserProfile


PROFILE_MAP = {
    RoleChoices.REGULAR: RegularUserProfile,
    RoleChoices.DOCTOR: Doctor,
    RoleChoices.AMBULANCE: AmbulanceProfile,
    RoleChoices.PHARMACY: PharmacyProfile,
    RoleChoices.DIAGNOSTIC: DiagnosticProfile,
    RoleChoices.BLOOD_DONOR: BloodDonor,
}