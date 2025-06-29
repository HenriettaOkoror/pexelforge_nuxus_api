from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('lead', 'Project Lead'),
        ('dev', 'Developer'),
    ]
    mfa_secret = models.CharField(null=True, blank=True)
    is_mfa_enabled = models.BooleanField(default=False)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField(null=True, blank=True)
    deadline = models.DateField()
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Assignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class Document(models.Model):
    projects = models.ManyToManyField(Project, related_name='documents')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


    def file_name(self):
        return self.file.name.split('/')[-1]
