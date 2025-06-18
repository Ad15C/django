import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, LoginForm, EditProfileForm
from django.utils import timezone
from mediatheque.staff.models import MediaStaff, StaffBorrowItem, BookStaff, CDStaff, DVDStaff, BoardGameStaff
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from mediatheque.authentification.decorators import role_required

logger = logging.getLogger(__name__)

User = get_user_model()


@login_required
def home_view(request):
    return render(request, 'authentification/client_dashboard.html')


def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Inscription réussie ! Vous êtes maintenant connecté.")
            return redirect('authentification:home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur sur {field}: {error}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'authentification/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)  # Connecter l'utilisateur
                messages.success(request, "Vous êtes connecté avec succès.")

                # Redirection vers la page appropriée en fonction du rôle de l'utilisateur
                if user.role == User.CLIENT:
                    return redirect('client:espace_client')
                elif user.role == User.STAFF:
                    return redirect('authentification:espace_staff')
                elif user.role == User.ADMIN:
                    return redirect('/admin/')

                # Si aucun rôle ne correspond, on redirige vers la page d'accueil par défaut
                return redirect('/')

            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = LoginForm()

    # Retourne le formulaire de connexion
    return render(request, 'authentification/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, "Vous êtes maintenant déconnecté.")
    return redirect('authentification:connexion')


@login_required
def edit_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # Vérifier si l'utilisateur modifie son propre profil ou est admin
    if request.user != user and request.user.role != User.ADMIN:
        messages.error(request, "Accès interdit.")
        return redirect('authentification:home')

    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('authentification:modifier_profil', user_id=user.id)
    else:
        form = EditProfileForm(instance=user)

    return render(request, 'authentification/edit_profile.html', {'form': form})


@login_required
@role_required(User.STAFF)
def staff_dashboard(request):
    if request.user.role != User.STAFF:
        return HttpResponseForbidden("Accès interdit")

    user = request.user
    current_borrows = StaffBorrowItem.objects.filter(
        user=user,
        is_returned=False,
        due_date__gte=timezone.now()
    ).exclude(media__can_borrow=False)

    overdue_borrows = StaffBorrowItem.objects.filter(
        user=user,
        is_returned=False,
        due_date__lt=timezone.now()
    ).exclude(media__can_borrow=False)

    all_books = BookStaff.objects.all().order_by('name')
    all_cds = CDStaff.objects.all().order_by('name')
    all_dvds = DVDStaff.objects.all().order_by('name')
    all_boardgames = BoardGameStaff.objects.all().order_by('name')

    all_media = list(all_books) + list(all_cds) + list(all_dvds) + list(all_boardgames)

    paginator = Paginator(all_media, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for media in page_obj:
        if not media.pk:
            logger.error(f"Erreur : Le média {media.name} n\'a pas de pk valide.")

    return render(request, 'authentification/staff_dashboard.html', {
        'current_borrows': current_borrows,
        'overdue_borrows': overdue_borrows,
        'page_obj': page_obj,
    })


@login_required
def login_redirect_view(request):
    if request.user.role == User.ADMIN:
        return redirect('/admin/')
    elif request.user.role == User.STAFF:
        return redirect('authentification:espace_staff')
    elif request.user.role == User.CLIENT:
        return redirect('client:espace_client')
    return redirect('authentification:home')
