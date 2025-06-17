from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from mediatheque.staff.models import MediaStaff, StaffBorrowItem, BoardGameStaff, BookStaff, DVDStaff, CDStaff
from mediatheque.staff.forms import BorrowMediaForm, BookForm, DVDForm, CDForm, BoardGameForm
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from mediatheque.staff.decorators import role_required
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

User = get_user_model()

MAX_BORROW_DURATION_DAYS = 7


@login_required
@role_required(User.STAFF)
def staff_dashboard(request):
    # Vérifie si l'utilisateur est un membre du personnel (staff)
    if not request.user.is_staff_user:
        return HttpResponseForbidden("Accès interdit")

    user = request.user

    # Filtrer les emprunts en cours pour cet utilisateur
    current_borrows = StaffBorrowItem.objects.filter(
        user=user,
        is_returned=False,
        due_date__gte=timezone.now()
    ).exclude(media__can_borrow=False).exclude(media__isnull=True)

    # Filtrer les emprunts en retard
    overdue_borrows = StaffBorrowItem.objects.filter(
        user=user,
        is_returned=False,
        due_date__lt=timezone.now()
    ).exclude(media__can_borrow=False).exclude(media__isnull=True)

    # Récupérer tous les objets des modèles concrets (livres, CDs, DVDs, jeux de société)
    all_books = BookStaff.objects.all().order_by('name')
    all_cds = CDStaff.objects.all().order_by('name')
    all_dvds = DVDStaff.objects.all().order_by('name')
    all_boardgames = BoardGameStaff.objects.all().order_by('name')

    # Combiner tous les résultats dans une seule liste
    all_media = list(all_books) + list(all_cds) + list(all_dvds) + list(all_boardgames)

    # Pagination des médias
    paginator = Paginator(all_media, 10)  # 10 médias par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Rendre le tableau de bord avec les emprunts et les médias paginés
    return render(request, 'authentification/staff_dashboard.html', {
        'current_borrows': current_borrows,
        'overdue_borrows': overdue_borrows,
        'page_obj': page_obj,  # Passe l'objet de pagination au template
    })


@login_required
@role_required(User.STAFF)
@permission_required('authentification.can_add_media', raise_exception=True)
def add_media(request):
    form_classes = {
        'book': BookForm,
        'dvd': DVDForm,
        'cd': CDForm,
        'board_game': BoardGameForm,
    }

    if request.method == 'POST':
        media_type = request.POST.get('media_type')
        form_class = form_classes.get(media_type)

        if form_class:
            form = form_class(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, f"{media_type.capitalize()} ajouté avec succès.")
                return redirect('staff:media_liste')
            else:
                messages.error(request, "Erreur lors de l\'ajout du média. Veuillez réessayer.")
        else:
            form = None
            messages.error(request, "Type de média invalide.")
    else:
        form = None

    return render(request, 'staff/media/add_media.html', {
        'form': form,
    })


@login_required
@role_required(User.STAFF)
@permission_required('staff.can_view_media', raise_exception=True)
def media_list(request):
    available_filter = request.GET.get('available', None)
    only_borrowable = request.GET.get('only_borrowable', '')

    # Filtrage de base
    if available_filter == "true":
        all_books = BookStaff.objects.filter(is_available=True)
        all_cds = CDStaff.objects.filter(is_available=True)
        all_dvds = DVDStaff.objects.filter(is_available=True)
        all_boardgames = BoardGameStaff.objects.filter(is_available=True)
    elif available_filter == "false":
        all_books = BookStaff.objects.filter(is_available=False)
        all_cds = CDStaff.objects.filter(is_available=False)
        all_dvds = DVDStaff.objects.filter(is_available=False)
        all_boardgames = BoardGameStaff.objects.filter(is_available=False)
    else:
        all_books = BookStaff.objects.all()
        all_cds = CDStaff.objects.all()
        all_dvds = DVDStaff.objects.all()
        all_boardgames = BoardGameStaff.objects.all()

    # Filtrage par type de média
    media_type_filter = request.GET.get('media_type', '')
    if media_type_filter:
        all_books = all_books.filter(media_type__icontains=media_type_filter)
        all_cds = all_cds.filter(media_type__icontains=media_type_filter)
        all_dvds = all_dvds.filter(media_type__icontains=media_type_filter)
        all_boardgames = all_boardgames.filter(media_type__icontains=media_type_filter)

    # Filtrage par empruntabilité
    if only_borrowable == "true":
        all_books = all_books.filter(can_borrow=True)
        all_cds = all_cds.filter(can_borrow=True)
        all_dvds = all_dvds.filter(can_borrow=True)
        all_boardgames = all_boardgames.filter(can_borrow=True)

    # Combine toutes les listes d'objets dans une seule
    all_media = list(all_books) + list(all_cds) + list(all_dvds) + list(all_boardgames)

    # Pagination
    paginator = Paginator(all_media, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Récupérer les IDs médias affichés dans la page
    media_ids = [media.pk for media in page_obj]

    # Récupérer emprunts actifs pour ces médias
    active_borrows = StaffBorrowItem.objects.filter(media_id__in=media_ids, is_returned=False)

    # Dictionnaire media_id -> emprunt actif
    borrow_dict = {borrow.media_id: borrow for borrow in active_borrows}

    # Ajouter l'attribut borrow_record et can_be_borrowed_by_user
    for media in page_obj:
        media.borrow_record = borrow_dict.get(media.pk)
        media.can_be_borrowed_by_user = media.is_borrowable_by(request.user)

        if media.borrow_record:
            media.borrower = media.borrow_record.user
        else:
            media.borrower = None

    context = {
        'media_type_filter': media_type_filter,
        'available_filter': available_filter,
        'available_filter_is_true': available_filter == "true",
        'available_filter_is_false': available_filter == "false",
        'only_borrowable': only_borrowable,
        'only_borrowable_checked': only_borrowable == "true",
        'page_obj': page_obj,
    }

    return render(request, 'staff/media/media_list.html', context)


@login_required
@role_required(User.STAFF)
@permission_required('staff.can_view_media', raise_exception=True)
def media_detail(request, pk):
    media = get_object_or_404(MediaStaff, pk=pk)
    return render(request, 'staff/media/media_detail.html', {'media': media})


@login_required
@role_required(User.STAFF)
@permission_required('authentification.can_borrow_media', raise_exception=True)
def borrow_media(request, pk):
    try:
        # Vérifie si l'utilisateur a la permission d'emprunter un média
        if not request.user.has_perm('authentification.can_borrow_media'):
            raise PermissionDenied

        # Vérifie si c'est un jeu de société
        try:
            media = BoardGameStaff.objects.get(pk=pk)
        except BoardGameStaff.DoesNotExist:
            media = get_object_or_404(MediaStaff, pk=pk)

        if isinstance(media, BoardGameStaff):
            messages.error(request, "Les jeux de société ne peuvent pas être empruntés.")
            return redirect('staff:media_liste')

        # Vérifie si l'utilisateur a des emprunts en retard ou a dépassé le nombre maximum d'emprunts
        result = check_borrowing_conditions(request, request.user, media)
        if result:
            return result

        # Calcule la date limite de retour
        due_date = timezone.now() + timezone.timedelta(days=7)

        # Utilise le formulaire d'emprunt
        if request.method == 'POST':
            form = BorrowMediaForm(request.POST, user=request.user)
            if form.is_valid():
                with transaction.atomic():
                    due_date = form.cleaned_data['due_date']
                    borrow_item = StaffBorrowItem.objects.create(
                        user=request.user,
                        media=media,
                        borrow_date=timezone.now(),
                        due_date=due_date
                    )
                    media.is_available = False
                    media.save()

                messages.success(request, "Média emprunté avec succès !")
                return redirect('staff:succes_emprunt', pk=borrow_item.pk)



        else:
            # Formulaire pré-rempli avec les informations du média
            form = BorrowMediaForm(initial={'media': media, 'due_date': due_date})

        # Retour page de confirmation avec le formulaire
        return render(request, 'staff/media/borrow_confirm.html', {
            'form': form,
            'media': media,
            'due_date': due_date,
        })

    except PermissionDenied:
        messages.error(request, "Vous n\'avez pas la permission d\'emprunter ce média.")
        return redirect('staff:espace_staff')


def has_overdue_borrowings(user):
    """Vérifie si l'utilisateur a des emprunts en retard"""
    return StaffBorrowItem.objects.filter(user=user, is_returned=False, due_date__lt=timezone.now()).exists()


def has_max_active_borrows(user):
    """Vérifie si l'utilisateur a atteint la limite de 3 emprunts actifs"""
    return StaffBorrowItem.objects.filter(user=user, return_date__isnull=True).count() >= 3


def check_borrowing_conditions(request, user, media):
    # Vérifie si l'utilisateur a des emprunts en retard
    if has_overdue_borrowings(user):
        messages.error(request, "Vous avez des emprunts en retard. Impossible d\'emprunter de nouveaux médias.")
        return redirect('staff:media_liste')

    # Vérifie si l'utilisateur a déjà 3 emprunts actifs
    if has_max_active_borrows(user):
        messages.error(request, "Vous avez atteint la limite de 3 emprunts.")
        return redirect('staff:media_liste')

    return False


# Confirmation de l'emprunt
@login_required
@role_required(User.STAFF)
@permission_required('authentification.can_borrow_media', raise_exception=True)
def confirm_borrow(request, pk):
    media = get_object_or_404(MediaStaff, id=pk)

    # Date limite de retour fixée à 7 jours à partir d'aujourd'hui
    due_date = timezone.now() + timezone.timedelta(days=7)

    if request.method == 'POST':
        # On transmet request.POST ET l'utilisateur au form
        form = BorrowMediaForm(request.POST, user=request.user)
        if form.is_valid():
            # Le form nettoyé contient media et due_date valides
            borrow_item = form.save(commit=False)  # Ne pas sauvegarder tout de suite
            borrow_item.user = request.user  # Attribuer l'utilisateur à l'emprunt
            borrow_item.save()  # Sauvegarder en base

            # Ici, tu peux aussi changer la disponibilité du média
            media.is_available = False
            media.save()

            # Redirection après confirmation pour éviter le repost du formulaire
            return redirect('staff:succes_emprunt', pk=media.id)
    else:
        # GET : initialisation du formulaire avec les champs cachés media et due_date
        form = BorrowMediaForm(initial={
            'media': media,
            'due_date': due_date,
        }, user=request.user)

    context = {
        'media': media,
        'due_date': due_date,
        'form': form,
    }
    return render(request, 'staff/media/borrow_confirm.html', context)


# Succès de l'emprunt
@login_required
@role_required(User.STAFF)
@permission_required('authentification.can_borrow_media', raise_exception=True)
def borrow_success(request, pk):
    borrow_item = get_object_or_404(StaffBorrowItem, pk=pk)
    media = borrow_item.media

    is_late = borrow_item.due_date and borrow_item.due_date < timezone.now()

    # Médias empruntés par le même user (non retournés)
    borrowed_media = MediaStaff.objects.filter(
        staff_borrows_media__user=borrow_item.user,
        staff_borrows_media__is_returned=False,
        is_available=False
    ).distinct()

    # Médias empruntables pour l'utilisateur (disponibles et pouvant être empruntés)
    borrowable_media = MediaStaff.get_borrowable_by(borrow_item.user)

    return render(request, 'staff/media/borrow_success.html', {
        'borrow_item': borrow_item,
        'media': media,
        'is_late': is_late,
        'borrowed_media': borrowed_media,
        'borrowable_media': borrowable_media,
        'user': request.user,
    })


# Détail d'un emprunt
@login_required
@role_required(User.STAFF)
@permission_required('authentification.can_view_borrow', raise_exception=True)
def borrow_detail(request, pk):
    try:
        borrow_item = StaffBorrowItem.objects.get(pk=pk)
    except StaffBorrowItem.DoesNotExist:
        messages.error(request, "L'emprunt que vous cherchez n'existe pas.")
        return redirect('staff:media_liste')

    BORROWABLE_TYPES = ['Book', 'DVD', 'CD']

    media = borrow_item.media

    if media.media_type in BORROWABLE_TYPES:
        borrowable_media = [media]
        media_to_display = media
    else:
        borrowable_media = []
        media_to_display = None  # NE PAS passer un média non empruntable

    user = borrow_item.user
    is_late = borrow_item.due_date < timezone.now() and not borrow_item.is_returned

    context = {
        'borrow_item': borrow_item,
        'media': media_to_display,
        'borrowable_media': borrowable_media,
        'user': user,
        'is_late': is_late,
    }

    return render(request, 'staff/media/borrow_detail.html', context)


@login_required
@role_required(User.STAFF)
@permission_required('authentification.can_return_media', raise_exception=True)
def return_media(request, pk):
    # Récupére l'élément d'emprunt
    borrow_item = get_object_or_404(StaffBorrowItem, pk=pk, is_returned=False)

    # Vérifie si un formulaire a été soumis avec un média sélectionné
    if request.method == 'POST':
        # Récupére l'ID du média sélectionné dans le formulaire
        media_id = request.POST.get('media')
        media = get_object_or_404(MediaStaff, pk=media_id)

        # Vérifier si ce média fait bien partie de cet emprunt
        if media == borrow_item.media:
            # Marque le média comme retourné
            borrow_item.is_returned = True
            borrow_item.return_date = timezone.now()
            borrow_item.save()

            # Rend le média à nouveau disponible
            media.is_available = True
            media.save()

            messages.success(request, f"Le média '{media.name}' a été retourné avec succès.")
        else:
            messages.error(request, "Ce média ne fait pas partie de cet emprunt.")

        return redirect('staff:detail_emprunt', pk=borrow_item.pk)  # Rediriger vers la page des détails de l'emprunt

    # Si l'utilisateur tente d'accéder à cette vue sans soumettre le formulaire (GET request)
    messages.error(request, "Veuillez sélectionner un média à retourner.")
    return redirect('staff:detail_emprunt', pk=borrow_item.pk)
