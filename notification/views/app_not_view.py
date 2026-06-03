from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from notification.models.app_notification_mod import AppNotification
from notification.serializers import AppNotificationSerializer
from core.decorators import api_exception_handler
from core.api_response import APIResponse


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):

    permission_classes = [IsAuthenticated]
    serializer_class = AppNotificationSerializer

    def get_queryset(self):
        return AppNotification.objects.filter(user=self.request.user)

    #  list all notifications (custom endpoint)
    @action(detail=False, methods=['get'])
    @api_exception_handler
    def all_app_notification(self, request):
        notifications = self.get_queryset()
        serializer = self.get_serializer(notifications, many=True)

        return Response(
            APIResponse.success(message="All Notification retrieve succefully",title="notifications",data=serializer.data),
            status=200
        )

    #  unread count
    @action(detail=False, methods=['get'])
    @api_exception_handler
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()

        return Response(
            APIResponse.success(message="All Unread Notification retrieve succefully",title="unread_count",data=count),
            status=200
        )

    #  mark all as read
    @action(detail=False, methods=['post'])
    @api_exception_handler
    def mark_all_read(self, request):
        self.get_queryset().filter(is_read=False).update(is_read=True)

        return Response(
            {"message": "All notifications marked as read"},
            status=200
        )