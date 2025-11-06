from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Follow
from .forms import CustomUserCreationForm, CustomUserUpdateForm

# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserUpdateForm

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Registrar CustomUser a l'admin. Reusem formularis personalitzats
    per crear i editar usuaris.
    """
    add_form = CustomUserCreationForm
    form = CustomUserUpdateForm
    model = CustomUser
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("display_name", "bio", "avatar")}),
    )