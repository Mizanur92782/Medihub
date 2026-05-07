from rest_framework.routers import DefaultRouter
from authentication.views import SignupViewSet

router = DefaultRouter()
router.register('signup', SignupViewSet, basename='signup')

urlpatterns = router.urls
