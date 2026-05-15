from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import json
from notification.models.push_not_model import Device
from notification.servcies import PushNotification


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_device(request):
    token = request.data.get("token")
    if not token:
        return JsonResponse({"error": "token required"}, status=400)
    device, created = Device.objects.get_or_create(
        token=token,
        defaults={"user": request.user}
    )
    # if token exists but belongs to different user, reassign
    if not created and device.user != request.user:
        device.user = request.user
        device.save()
    return JsonResponse({"registered": True, "created": created})
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_push(request):
    token = request.data.get("token")
    if token:
        response = PushNotification.send_to_token(
            token, "Test Notification", "Hi Brothers!"
        )
        return JsonResponse({"message_id": response})
        
    # send to all devices of the logged-in user
    results = PushNotification.send_to_user(
        request.user, "Test Notification", "Push notification from Medihub is working!"
    )
    return JsonResponse({"sent": len(results), "message_ids": results})
