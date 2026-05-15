from rest_framework import serializers
from notification.models.app_notification_mod import AppNotification
from authentication.models import User


''' App notification - 3: serializer for getting notification'''
class AppNotificationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = AppNotification
        fields = ["user", "title", "message",'is_read']