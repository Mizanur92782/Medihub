import random

from django.db.models import Count
from django.utils import timezone

from profiles.models.doctor_prof_mod import Doctor
from interactions.models.user_docotor_interaction import (
    UserDoctorInterest,
    DoctorFeedImpression,
)
from feed.weight_formula import WEIGHTS


class DoctorFeedEngine:

    def __init__(self, user):
        self.user = user

    def generate_feed(self, queryset=None):
        doctors = (queryset or Doctor.objects).select_related(
            "specialization", "division", "district", "evaluation"
        )

        # bulk-fetch to avoid N+1
        interests = {
            i.specialization_id: i.score
            for i in UserDoctorInterest.objects.filter(user=self.user)
        }
        impression_counts = {
            i["doctor_id"]: i["total"]
            for i in DoctorFeedImpression.objects
            .filter(user=self.user)
            .values("doctor_id")
            .annotate(total=Count("id"))
        }

        result = [
            {"doctor": d, "score": self.calculate_score(d, interests, impression_counts)}
            for d in doctors
        ]

        result.sort(key=lambda x: x["score"], reverse=True)
        return self.apply_exploration(result)

    def calculate_score(self, doctor, interests, impression_counts):
        stats = getattr(doctor, "evaluation", None)
        if not stats:
            return 0

        score = self.base_score(stats)
        score += self.personalization_score(doctor, interests)
        score += self.location_score(doctor)
        score += self.quality_score(stats)
        score += self.activity_score(stats)
        score += self.trending_score(stats)
        score += self.new_doctor_boost(doctor)
        score -= self.repetition_penalty(doctor, impression_counts)
        return round(score, 2)

    def base_score(self, stats):
        return (
            stats.total_profile_views * WEIGHTS["profile_views"] * 0.1 +
            stats.total_followers    * WEIGHTS["followers"] * 0.6 +
            stats.total_questions    * WEIGHTS["questions"]  * 0.5 +
            stats.total_booking      * WEIGHTS["booking"]
        )

    def personalization_score(self, doctor, interests):
        score = interests.get(doctor.specialization_id, 0)
        return score * WEIGHTS["same_specialization"] * 0.25

    def location_score(self, doctor):
        user_profile = getattr(self.user, "regularuserprofile", None)
        if not user_profile:
            return 0
        if user_profile.district_id == doctor.district_id:
            return WEIGHTS["nearby"]
        if user_profile.division_id == doctor.division_id:
            return WEIGHTS["nearby"] * 0.4
        return 0

    def quality_score(self, stats):
        score = stats.avg_rating * WEIGHTS["rating"]
        if stats.is_verified:
            score += WEIGHTS["verified"]
        if stats.profile_completed:
            score += 10
        return score

    def activity_score(self, stats):
        score = 0
        if stats.is_online:
            score += WEIGHTS["online"]
        if stats.last_active:
            diff = timezone.now() - stats.last_active
            if diff.days <= 1:
                score += 5
        return score

    def trending_score(self, stats):
        return stats.total_feed_click * 0.5

    def new_doctor_boost(self, doctor):
        diff = timezone.now() - doctor.created
        if diff.days <= 30:
            return WEIGHTS["new_doctor_boost"]
        return 0

    def repetition_penalty(self, doctor, impression_counts):
        count = impression_counts.get(doctor.id, 0)
        return count * abs(WEIGHTS["repeat_penalty"]) * 0.2

    def apply_exploration(self, result):
        top = result[:30]
        for item in top:
            item["score"] += random.uniform(0, 2)
        top.sort(key=lambda x: x["score"], reverse=True)
        return top + result[30:]