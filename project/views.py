from rest_framework import viewsets, permissions
from .models import Project, Assignment, Document, User
from django.utils import timezone
from .serializers import (
    ProjectSerializer, AssignmentSerializer, DocumentSerializer, 
    CustomTokenObtainPairSerializer, UserViewSetSerializer, DocumentCreateSerializer
    )
from rest_framework_simplejwt.views import TokenObtainPairView



class IsAdminUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff or request.method in permissions.SAFE_METHODS


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserViewSetSerializer
    # permission_classes = [IsAdminUserOrReadOnly]


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'admin'

class IsProjectLead(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'lead'

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_permissions(self):
        if self.request.method in ['POST', 'DELETE']:
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]

class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsProjectLead]

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def get_serializer(self, *args, **kwargs):
        if self.request.method == 'POST':
            return DocumentCreateSerializer(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(
            uploaded_by=self.request.user,
            uploaded_at=timezone.now()
        )
