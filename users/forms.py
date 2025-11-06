# users/forms.py
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth.password_validation import validate_password, password_validators_help_text_html
from .models import CustomUser

class CustomUserCreationForm(forms.ModelForm):
    """
    Formulari de registre. Mostra help_text generat per Django pels validadors de contrasenya.
    Inclou validacions: email únic, username amb regex, contrasenyes coincidents i complexitat.
    """
    password1 = forms.CharField(
        label="Contrasenya",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Introdueix una contrasenya segura"}),
        help_text=password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="Confirmar contrasenya",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Repeteix la contrasenya"}),
    )

    class Meta:
        model = CustomUser
        fields = ["username", "email", "first_name", "last_name"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom d'usuari"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Correu electrònic"}),
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Cognoms"}),
        }

    def clean_username(self):
        username = self.cleaned_data["username"]
        validator = RegexValidator(r"^[\w.@+-]+$", "Nom d'usuari invàlid (només lletres, números i @/./+/-/_).")
        validator(username)
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise ValidationError("Aquest nom d'usuari ja existeix.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise ValidationError("Aquest correu ja està registrat.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            raise ValidationError("Les contrasenyes no coincideixen.")
        if p1:
            # Aquest llançarà ValidationError amb motius si falla (p.ex. <8 chars)
            validate_password(p1)
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])  # fa hashing
        if commit:
            user.save()
        return user


class CustomUserUpdateForm(forms.ModelForm):
    """
    Formulari per editar perfil: first/last name, display_name, bio i avatar.
    Widgets amb classes Bootstrap per un estil coherent.
    """
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "display_name", "bio", "avatar"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "display_name": forms.TextInput(attrs={"class": "form-control"}),
        }


class CustomAuthenticationForm(AuthenticationForm):
    """
    Permet iniciar sessió amb username o email.
    """
    username = forms.CharField(
        label="Usuari o correu electrònic",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Usuari o correu electrònic"}),
    )
    password = forms.CharField(
        label="Contrasenya",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Contrasenya"}),
    )

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:
            # Si l'entrada sembla un email, provem a buscar user per email i usar username
            try:
                user_obj = CustomUser.objects.get(email__iexact=username)
                username = user_obj.username
            except CustomUser.DoesNotExist:
                pass

            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise ValidationError("Credencials incorrectes.")
        return self.cleaned_data
