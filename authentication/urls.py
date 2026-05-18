from rest_framework.routers import DefaultRouter
from authentication.views import SignupViewSet, LoginViewSet, LogoutViewSet, PasswordResetViewSet

router = DefaultRouter()
router.register('signup',          SignupViewSet,        basename='signup')
router.register('auth',            LoginViewSet,         basename='auth')
router.register('auth',            LogoutViewSet,        basename='auth-logout')
router.register('password-reset',  PasswordResetViewSet, basename='password-reset')

urlpatterns = router.urls
