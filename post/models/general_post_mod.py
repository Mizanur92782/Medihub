from django.db import models
from django.conf import settings
from location.models import Division, District, Upozila
from core.enum import PostStatusChoices


class GeneralPost(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='general_posts')

    title = models.CharField(max_length=300)
    content = models.TextField()
    image = models.ImageField(upload_to='post/general/', blank=True, null=True)

    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    upozila = models.ForeignKey(Upozila, on_delete=models.SET_NULL, null=True, blank=True)

    contact_number = models.CharField(max_length=15, blank=True, null=True)
    status = models.CharField(max_length=15, choices=PostStatusChoices.choices, default=PostStatusChoices.OPEN)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.title} by {self.user}'
