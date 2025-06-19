from django.contrib import admin
from .models import User, Project, Assignment, Document
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User  # Make sure you're importing your custom user model


@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Security'), {'fields': ('mfa_secret', 'is_mfa_enabled')}),
        ('Role Info', {'fields': ('role',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    exclude = ('groups', 'user_permissions')
    list_display = ('username', 'email', 'role', 'is_mfa_enabled', 'is_staff', 'is_active')


admin.site.register(Project)
admin.site.register(Assignment)
admin.site.register(Document)
