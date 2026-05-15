from django.db import models
from authentication.models import User


class Device(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices', null=True, blank=True)
    token = models.CharField(max_length=500, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.token[:30]}"
