"""
URL configuration for medihub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from medihub.health_check import HealthCheck
from medihub.queue_dashboard import queue_dashboard, TeshMessageQuee
from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title='Medihub API',
        default_version='v1',
        description='Medihub platform API documentation',
        contact=openapi.Contact(email='admin@medihub.com'),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

def serve_sw(request):
    content = render_to_string('firebase-messaging-sw.js')
    return HttpResponse(content, content_type='application/javascript')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('firebase-messaging-sw.js', serve_sw),
    path('', HealthCheck),
    path('health/', HealthCheck),
    path('queue/dashboard/', queue_dashboard, name='queue-dashboard'),
    path('queue/test/', TeshMessageQuee, name='queue-test'),
    path('', include('django_prometheus.urls')),
    path('authentication/', include('authentication.urls')),
    path('location/', include('location.urls')),
    path('notification/', include('notification.urls')),
    path('', include('feed.urls')),

    # Swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
    
]
