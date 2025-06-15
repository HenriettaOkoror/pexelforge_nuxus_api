from django.contrib import admin
from .models import User, Project, Assignment, Document
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    fieldsets = DefaultUserAdmin.fieldsets + (
        ('Role Info', {'fields': ('role',)}),
    )
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')

admin.site.register(Project)
admin.site.register(Assignment)
admin.site.register(Document)
