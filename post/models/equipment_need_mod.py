from django.db import models
from django.conf import settings
from location.models import Division, District, Upozila
from core.enum import PostStatusChoices, UrgencyChoices, EquipmentConditionChoices


class EquipmentNeedPost(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='equipment_need_posts')

    equipment_name = models.CharField(max_length=300)
    quantity = models.CharField(max_length=100)
    condition = models.CharField(max_length=10, choices=EquipmentConditionChoices.choices, default=EquipmentConditionChoices.GOOD)
    image = models.ImageField(upload_to='post/equipment/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    # User location
    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    upozila = models.ForeignKey(Upozila, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.TextField(blank=True, null=True)

    contact_number = models.CharField(max_length=15)
    urgency = models.CharField(max_length=10, choices=UrgencyChoices.choices, default=UrgencyChoices.MEDIUM)
    status = models.CharField(max_length=15, choices=PostStatusChoices.choices, default=PostStatusChoices.OPEN)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.equipment_name} needed by {self.user}'
