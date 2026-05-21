import django_filters

from profiles.models.doctor_prof_mod import Doctor


class DoctorFeedFilter(django_filters.FilterSet):

    division       = django_filters.NumberFilter(field_name="division_id")
    district       = django_filters.NumberFilter(field_name="district_id")
    specialization = django_filters.NumberFilter(field_name="specialization_id")

    class Meta:
        model  = Doctor
        fields = ["division", "district", "specialization"]
