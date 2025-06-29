import pyotp
from rest_framework import serializers
from .models import User, Project, Assignment, Document
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

UserModel = get_user_model()


class BaseUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = UserModel
        fields = ['id', 'username', 'email', 'password', 'role']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = UserModel(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserViewSetSerializer(BaseUserSerializer):
    pass


class UserCreateSerializer(BaseUserSerializer):
    password = serializers.CharField(write_only=True, required=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'username', 'email', 'role']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    mfa_code = serializers.CharField(required=False)

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        # If MFA is enabled, verify code
        if user.is_mfa_enabled:
            totp = pyotp.TOTP(user.mfa_secret)
            print("Expected code:", totp.now())
            mfa_code = attrs.get("mfa_code")
            if not mfa_code:
                raise serializers.ValidationError({"detail": "MFA code required."})

            totp = pyotp.TOTP(user.mfa_secret)
            if not totp.verify(mfa_code, valid_window=1):
                raise serializers.ValidationError({"detail": "Invalid MFA code."})

        data['role'] = user.role
        return data


class ProjectSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'

    def get_members(self, obj):
            objs = Assignment.objects.filter(project=obj).values_list('user__username', flat=True)
            return objs
    

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'


class AssignmentCreateSerializer(serializers.Serializer):
    users = serializers.ListField(child=serializers.IntegerField())
    project = serializers.IntegerField()

    def create(self, validated_data):
        user_ids = validated_data.get('users', [])
        project_id = validated_data.get('project')

        if not user_ids or not project_id:
            raise serializers.ValidationError("Both 'users' and 'project' are required.")

        Assignment.objects.filter(project_id=project_id).delete()
        Assignment.objects.bulk_create([
            Assignment(user_id=user_id, project_id=project_id)
            for user_id in user_ids
        ])
        return {"project": project_id, "assigned_users": user_ids}
    

class DocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = ('id', 'file', 'uploaded_by', 'uploaded_at','projects')

        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['projects'] = [{'name': instance.name, 'id': instance.id} for instance in instance.projects.all()]
        return data


class DocumentCreateSerializer(serializers.ModelSerializer):
    projects = serializers.ListField(child=serializers.IntegerField())
    class Meta:
        model = Document
        exclude = ('uploaded_by', 'uploaded_at', 'project')
        write_only_fields = ('projects',)


    def create(self, validated_data):
        projects = validated_data.pop('projects', None)
        documents = []
        for project_id in projects:
            validated_data['project'] = Project.objects.get(id=project_id)
            validated_data['uploaded_by'] = self.context['request'].user
            document = super().create(validated_data.copy())  # use copy to avoid mutation issues
            documents.append(document)
        return documents   
    
    def update(self, instance, validated_data):
        projects = validated_data.pop('projects', None)
        if projects:
            for project_id in projects:
                Document.objects.create(
                    file=instance.file,
                    uploaded_by=instance.uploaded_by,
                    project=Project.objects.get(id=project_id)
                )
                instance.project = Project.objects.get(id=project_id)
                instance.save()
        return instance
