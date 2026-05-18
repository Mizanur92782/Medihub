from django.db import models
from django.conf import settings
from location.models import Division, District, Upozila
from core.enum import BloodGroupChoices, GenderChoices, PostStatusChoices, UrgencyChoices


class BloodNeedPost(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blood_need_posts')

    # Patient info
    patient_name = models.CharField(max_length=200)
    patient_age = models.PositiveSmallIntegerField()
    patient_gender = models.CharField(max_length=10, choices=GenderChoices.choices)
    blood_group = models.CharField(max_length=5, choices=BloodGroupChoices.choices)
    bags_needed = models.PositiveSmallIntegerField(default=1)

    # Location
    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    upozila = models.ForeignKey(Upozila, on_delete=models.SET_NULL, null=True, blank=True)
    hospital_name = models.CharField(max_length=300)
    hospital_address = models.TextField(blank=True, null=True)

    # When needed
    needed_date = models.DateField()
    needed_time = models.TimeField()

    # Contact
    contact_number = models.CharField(max_length=15)

    urgency = models.CharField(max_length=10, choices=UrgencyChoices.choices, default=UrgencyChoices.HIGH)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=15, choices=PostStatusChoices.choices, default=PostStatusChoices.OPEN)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.blood_group} needed for {self.patient_name} at {self.hospital_name}'
