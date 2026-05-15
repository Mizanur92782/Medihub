from django.urls import path
from notification.views.push_notf_view import register_device, test_push
from django.shortcuts import render

urlpatterns = [
    path('device/register/', register_device, name='register-device'),
    path('push/test/', test_push, name='test-push'),
    path('push/tester/', lambda req: render(req, 'push_test.html'), name='push-tester'),
]
