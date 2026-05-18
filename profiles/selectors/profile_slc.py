from authentication.models import User
from cache.services.user_services import UserProfileCacheServies
from profiles.models import (
    RegularUserProfile, Doctor, AmbulanceProfile,
    PharmacyProfile, DiagnosticProfile, BloodDonor
)
from core.enum import RoleChoices


PROFILE_MAP = {
    RoleChoices.REGULAR: RegularUserProfile,
    RoleChoices.DOCTOR: Doctor,
    RoleChoices.AMBULANCE: AmbulanceProfile,
    RoleChoices.PHARMACY: PharmacyProfile,
    RoleChoices.DIAGNOSTIC: DiagnosticProfile,
    RoleChoices.BLOOD_DONOR: BloodDonor,
}


class UserProfileSelectors:

    @staticmethod
    def GetProfile(user_id):
        cache = UserProfileCacheServies.GetProfile(user_id)
        if cache:
            return cache
       
        # if profile doesnt exist in cache ,retrieve from database
        user = User.objects.get(id=user_id)
        model = PROFILE_MAP.get(user.user_type)
        if model is None:
            return None

        profile = model.objects.get(user=user)
        UserProfileCacheServies.SetProfile(user_id, profile)
        return profile
        