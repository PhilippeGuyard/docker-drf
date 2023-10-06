"""
Django Admin customization
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

from core import models


class UserAdmin(DefaultUserAdmin):
    ordering = ["id"]
    list_display = ["email", "name"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("name",)}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (None,
         {"classes": ("wide",), "fields": ("email", "password1", "password2")}
         ),
    )
    readonly_fields = ("last_login",)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "name",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )


admin.site.register(models.User, UserAdmin)
