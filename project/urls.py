from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import(
    ProjectViewSet, AssignmentViewSet, DocumentViewSet, 
    CustomTokenObtainPairView, UserViewSet,
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
    path('', include(router.urls)),
]
