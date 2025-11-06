# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomUserUpdateForm, CustomAuthenticationForm
from .models import CustomUser

def register_view(request):
    """
    GET: mostra el formulari de registre.
    POST: valida i crea l'usuari; login automàtic i redirecció a perfil.
    """
    if request.user.is_authenticated:
        messages.info(request, "Ja estàs autenticat.")
        return redirect('users:profile')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registre completat. Benvingut/da!")
            return redirect('users:profile')
        else:
            messages.error(request, "Hi ha errors al formulari. Revisa'ls.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    """
    Login amb username o email. Si hi ha ?next=... redirigeix-hi.
    """
    if request.user.is_authenticated:
        return redirect('users:profile')

    form = CustomAuthenticationForm(request=request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        messages.success(request, "Sessió iniciada.")
        next_url = request.POST.get('next') or request.GET.get('next')
        return redirect(next_url or 'users:profile')
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "S'ha tancat la sessió.")
    return redirect('home')

@login_required
def profile_view(request):
    return render(request, 'users/profile.html')

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualitzat.")
            return redirect('users:profile')
        else:
            messages.error(request, "Hi ha errors al formulari.")
    else:
        form = CustomUserUpdateForm(instance=request.user)
    return render(request, 'users/edit_profile.html', {'form': form})

def public_profile_view(request, username):
    user_obj = get_object_or_404(CustomUser, username=username)
    return render(request, 'users/public_profile.html', {'profile_user': user_obj})
