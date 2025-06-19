from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import(
    ProjectViewSet, AssignmentViewSet, DocumentViewSet, MFADisableView, MFAStatusView,
    CustomTokenObtainPairView, UserViewSet, ChangePasswordView, ResetPasswordView, MFASetupView
)
from rest_framework_simplejwt.views import (
    TokenRefreshView, 
)

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'assignments', AssignmentViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('auth/reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('auth/mfa/setup/', MFASetupView.as_view(), name='mfa_setup'),
    path("auth/mfa/status/", MFAStatusView.as_view(), name="mfa_status"),
    path("auth/mfa/disable/", MFADisableView.as_view(), name="mfa_status"),
    path('', include(router.urls)),
]
