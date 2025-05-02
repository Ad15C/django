from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, LoginForm, EditProfileForm
from django.utils import timezone
from staff.models import StaffBorrowItem, MediaStaff
from django.contrib.auth import get_user_model
from functools import wraps

User = get_user_model()


# Décorateur pour vérifier le rôle
def role_required(role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role != role:
                messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette page.")
                return redirect('home')
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


@login_required
def home_view(request):
    return render(request, 'authentification/home.html')


# Inscription
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Inscription réussie ! Vous êtes maintenant connecté.")
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur sur {field}: {error}")
    else:
        form = CustomUserCreationForm()

    return render(request, 'authentification/signup.html', {'form': form})


# Connexion
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Vous êtes connecté avec succès.")
                if user.role == User.STAFF:
                    return redirect('espace_staff')
                elif user.role == User.CLIENT:
                    return redirect('espace_client')
                else:
                    return redirect('home')
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = LoginForm()

    return render(request, 'authentification/login.html', {'form': form})


# Déconnexion
def logout_view(request):
    logout(request)
    messages.success(request, "Vous êtes maintenant déconnecté.")
    return redirect('login')


# Mise à jour du profil
@login_required
def edit_profile(request):
    user = request.user
    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirige vers une page de profil après modification
    else:
        form = EditProfileForm(instance=user)

    return render(request, 'edit_profile.html', {'form': form})

# Espace client
@login_required
@role_required(User.CLIENT)
def client_dashboard(request):
    borrows = StaffBorrowItem.objects.filter(user=request.user, is_returned=False).select_related('media')
    available_media = MediaStaff.objects.filter(can_borrow=True, available=True)

    return render(request, "authentification/espace_client.html", {
        'borrows': borrows,
        'available_media': available_media
    })


# Espace staff
@login_required
@role_required(User.STAFF)
def staff_dashboard(request):
    borrows = StaffBorrowItem.objects.filter(is_returned=False).select_related('media')
    overdue_borrows = StaffBorrowItem.objects.filter(is_returned=False, due_date__lt=timezone.now()).select_related(
        'media')
    all_media = MediaStaff.objects.all()

    return render(request, "authentification/espace_staff.html", {
        'borrows': borrows,
        'overdue_borrows': overdue_borrows,
        'all_media': all_media
    })


# Redirection après login
@login_required
def login_redirect_view(request):
    if request.user.role == User.ADMIN:
        return redirect('/admin/')  # Ou reverse('admin:index')
    elif request.user.role == User.STAFF:
        return redirect('espace_staff')
    elif request.user.role == User.CLIENT:
        return redirect('espace_client')
    return redirect('home')
