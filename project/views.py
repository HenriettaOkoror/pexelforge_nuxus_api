from rest_framework import viewsets, permissions
from .models import Project, Assignment, Document, User
from .serializers import (
    ProjectSerializer, AssignmentSerializer, DocumentSerializer, 
    CustomTokenObtainPairSerializer, UserViewSetSerializer,
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

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
