from rest_framework.routers import DefaultRouter
from feed.views import DoctorFeedViewSet

router = DefaultRouter()
router.register("feed", DoctorFeedViewSet, basename="feed")

urlpatterns = router.urls
