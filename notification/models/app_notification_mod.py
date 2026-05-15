from django.db import models
from authentication.models import User 



'''AppNotification -1: store app notification in database for crud operatioon '''
class AppNotification(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='app_notification'
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user"], name="appnotif_user_idx"),
            models.Index(fields=["created_at"], name="appnotif_created_idx"),
        ]

    def __str__(self):
        return self.title