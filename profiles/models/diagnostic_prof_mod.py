from django.db import models
from django.conf import settings
from location.models import District, Division, Upozila


class DiagnosticProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='diagnostic')
    diagnostic_name = models.CharField(max_length=200)
    owner_name = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=15)
    license_number = models.CharField(max_length=100, unique=True)
    license_validity = models.DateField()
    is_open = models.BooleanField(default=True)

    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    upozila = models.ForeignKey(Upozila, on_delete=models.SET_NULL, null=True)
    address = models.TextField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.diagnostic_name} - {self.owner_name}'
