from rest_framework import serializers

from profiles.models.doctor_prof_mod import Doctor


class DoctorFeedCardSerializer(serializers.ModelSerializer):

    specialization = serializers.StringRelatedField()
    division       = serializers.StringRelatedField()
    district       = serializers.StringRelatedField()
    full_name      = serializers.SerializerMethodField()

    # stats from related DoctorStats (evaluation)
    avg_rating        = serializers.FloatField(source="evaluation.avg_rating",        default=0)
    total_followers   = serializers.IntegerField(source="evaluation.total_followers", default=0)
    total_booking     = serializers.IntegerField(source="evaluation.total_booking",   default=0)
    is_verified       = serializers.BooleanField(source="evaluation.is_verified",     default=False)
    is_online         = serializers.BooleanField(source="evaluation.is_online",       default=False)
    profile_completed = serializers.BooleanField(source="evaluation.profile_completed", default=False)

    feed_score = serializers.FloatField(default=0)

    class Meta:
        model  = Doctor
        fields = [
            "id", "full_name", "profile_dp",
            "specialization", "division", "district",
            "years_of_experience",
            "avg_rating", "total_followers", "total_booking",
            "is_verified", "is_online", "profile_completed",
            "feed_score",
        ]

    def get_full_name(self, obj):
        parts = [obj.first_name, obj.middle_name, obj.last_name]
        return " ".join(p for p in parts if p)
