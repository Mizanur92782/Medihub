from django.db.models import Avg

from interactions.models.user_docotor_interaction import (
    UserDoctorInteractionAskQuestion,
    UserDoctorInteractionFollwDoctor,
    UserDoctorInteractionProfileShow,
)
from profiles.models.doctor_prof_mod import DoctorRating, DoctorStats


class DoctorStatService:

    @staticmethod
    def update_doctor_stats(doctor):
        stats, _ = DoctorStats.objects.get_or_create(doctor=doctor)

        stats.total_profile_views = UserDoctorInteractionProfileShow.objects.filter(
            doctor=doctor
        ).count()

        stats.total_followers = UserDoctorInteractionFollwDoctor.objects.filter(
            doctor=doctor, follow=True
        ).count()

        stats.total_questions = UserDoctorInteractionAskQuestion.objects.filter(
            doctor=doctor
        ).count()

        ratings = DoctorRating.objects.filter(doctor=doctor)
        stats.avg_rating = ratings.aggregate(avg=Avg("rating"))["avg"] or 0
        stats.total_rating = ratings.count()

        stats.save()