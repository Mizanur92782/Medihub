from django.db import models
from django.conf import settings
from location.models import District, Division, Upozila
from core.enum import BloodGroupChoices, AvailabilityChoices, GenderChoices


class BloodDonor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blood_donor')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GenderChoices.choices)
    contact_number = models.CharField(max_length=15)

    blood_group = models.CharField(max_length=5, choices=BloodGroupChoices.choices)
    availability = models.CharField(max_length=15, choices=AvailabilityChoices.choices, default=AvailabilityChoices.AVAILABLE)
    last_donated = models.DateField(blank=True, null=True)

    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    upozila = models.ForeignKey(Upozila, on_delete=models.SET_NULL, null=True)

    address = models.TextField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.blood_group}'
