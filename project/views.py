import pyotp
import base64
import qrcode
from io import BytesIO
from qrcode.image.pil import PilImage
from rest_framework import viewsets, permissions, status
from .models import Project, Assignment, Document, User
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import (
    ProjectSerializer, AssignmentSerializer, DocumentSerializer, AssignmentCreateSerializer,
    CustomTokenObtainPairSerializer, UserViewSetSerializer, DocumentCreateSerializer
    )
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .utils import logout_all_sessions
from django.core.mail import send_mail



class IsAdminUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff or request.method in permissions.SAFE_METHODS


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserViewSetSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['role']
    # permission_classes = [IsAdminUserOrReadOnly]

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not user.check_password(old_password):
            return Response({"detail": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        logout_all_sessions(user)
        return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("pssword")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        user.set_password(password)
        user.save()

        # Send password reset email
        send_mail(
            subject="Your Password Has Been Reset",
            message=f"Your new password is: {password}",
            from_email="noreply@example.com",
            recipient_list=[email],
        )
        return Response({"detail": "Password sent to your email."}, status=status.HTTP_200_OK)


class MFASetupView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        totp = pyotp.TOTP(pyotp.random_base32())
        user.mfa_secret = totp.secret
        user.save()

        otp_auth_url = totp.provisioning_uri(name=user.email, issuer_name="pixel_forge")

        # Specify PIL image factory to avoid TypeError
        img = qrcode.make(otp_auth_url, image_factory=PilImage)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return Response({"qr_code": f"data:image/png;base64,{img_str}"})


class MFADisableView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        print(user)
        user.mfa_secret = None
        user.is_mfa_enabled = False
        user.save()
        return Response({"detail": "MFA disabled successfully"})

class MFAStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"enabled": bool(request.user.mfa_secret)})
    

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
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['project_id']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AssignmentCreateSerializer
        return AssignmentSerializer

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == 'POST':
            return DocumentCreateSerializer
        return DocumentSerializer

    def perform_create(self, serializer):
        serializer.save(
            uploaded_by=self.request.user,
            uploaded_at=timezone.now()
        )
