from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.utils.translation import gettext_lazy as _

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("email", "phone", "is_verified", "is_staff", "is_superuser")
    list_filter = ("is_staff", "is_superuser", "is_verified")

    fieldsets = (
        (None, {"fields": ("email", "phone", "password")}),
        (_("Permissions"), {"fields": ("is_active", "is_verified", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "phone", "password1", "password2", "is_verified", "is_staff", "is_superuser"),
        }),
    )

    search_fields = ("email", "phone")
    ordering = ("email",)
