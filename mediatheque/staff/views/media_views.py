from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from staff.models import MediaStaff, StaffBorrowItem, BoardGameStaff, BookStaff, DVDStaff, CDStaff
from staff.forms import MediaForm, BoardGameForm, BookForm, CDForm, DVDForm, BorrowMediaForm
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden

MAX_BORROW_DURATION_DAYS = 7


@login_required
def staff_dashboard(request):
    if not request.user.is_staff_user:  # Vérifie que l'utilisateur est membre du personnel
        return HttpResponseForbidden("Vous n'êtes pas autorisé à voir cette page.")

    user = request.user
    # Filtre les emprunts en cours pour cet utilisateur
    current_borrows = StaffBorrowItem.objects.filter(
        user=user,
        is_returned=False,
        due_date__gte=timezone.now()
    ).exclude(media__can_borrow=False).exclude(media__isnull=True)

    for borrow in current_borrows:
        print(f"Emprunt ID: {borrow.pk}, Média: {borrow.media.name}, Due Date: {borrow.due_date}")

    # Filtre les emprunts en retard
    overdue_borrows = StaffBorrowItem.objects.filter(
        user=user,
        is_returned=False,
        due_date__lt=timezone.now()
    ).exclude(media__can_borrow=False).exclude(media__isnull=True)

    # Récupére tous les objets des modèles concrets (livres, CDs, DVDs, jeux de société)
    all_books = BookStaff.objects.all().order_by('name')
    all_cds = CDStaff.objects.all().order_by('name')
    all_dvds = DVDStaff.objects.all().order_by('name')
    all_boardgames = BoardGameStaff.objects.all().order_by('name')

    # Combine tous les résultats dans une seule liste
    all_media = list(all_books) + list(all_cds) + list(all_dvds) + list(all_boardgames)
    paginator = Paginator(all_media, 10)  # 10 médias par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'authentification/staff_dashboard.html', {
        'current_borrows': current_borrows,
        'overdue_borrows': overdue_borrows,
        'page_obj': page_obj,  # Passe l'objet de pagination au template
    })


@permission_required('authentification.can_add_media', raise_exception=True)
def add_media(request):
    if request.method == 'POST':
        # Initialisation des formulaires spécifiques
        book_form = BookForm(request.POST) if 'is_book' in request.POST else None
        dvd_form = DVDForm(request.POST) if 'is_dvd' in request.POST else None
        cd_form = CDForm(request.POST) if 'is_cd' in request.POST else None
        board_game_form = BoardGameForm(request.POST) if 'is_board_game' in request.POST else None

        # La boucle factorisée
        for form, success_message in [
            (book_form, "Livre ajouté avec succès."),
            (dvd_form, "DVD ajouté avec succès."),
            (cd_form, "CD ajouté avec succès."),
            (board_game_form, "Jeu de société ajouté avec succès."),
        ]:
            if form and form.is_valid():
                form.save()
                messages.success(request, success_message)
                return redirect('staff:media_liste')

    else:
        # Initialisation des formulaires vides pour le GET
        book_form = BookForm()
        dvd_form = DVDForm()
        cd_form = CDForm()
        board_game_form = BoardGameForm()

    # Rendu du template
    return render(request, 'staff/media/add_media.html', {
        'book_form': book_form,
        'dvd_form': dvd_form,
        'cd_form': cd_form,
        'board_game_form': board_game_form,
    })


@permission_required('authentification.can_view_media', raise_exception=True)
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
        all_books = all_books.filter(is_borrowable=True)
        all_cds = all_cds.filter(is_borrowable=True)
        all_dvds = all_dvds.filter(is_borrowable=True)
        all_boardgames = all_boardgames.filter(is_borrowable=True)

    # Combine toutes les listes d'objets dans une seule
    all_media = list(all_books) + list(all_cds) + list(all_dvds) + list(all_boardgames)

    # Pagination
    paginator = Paginator(all_media, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Ajout de la propriété personnalisée
    for item in page_obj:
        item.can_be_borrowed_by_user = item.is_borrowable_by(request.user)

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


@permission_required('authentification.can_view_media', raise_exception=True)
def media_detail(request, pk):
    media = get_object_or_404(MediaStaff, pk=pk)
    return render(request, 'staff/media/media_detail.html', {'media': media})


@permission_required('authentification.can_borrow_media', raise_exception=True)
def borrow_media(request, pk):
    media = get_object_or_404(MediaStaff, pk=pk)

    # Vérifie si c'est un jeu de société
    if isinstance(media, BoardGameStaff):
        messages.error(request, "Les jeux de société ne peuvent pas être empruntés.")
        return redirect('staff:media_liste')

    # Vérifie si l'utilisateur a des emprunts en retard
    if StaffBorrowItem.objects.filter(user=request.user, is_returned=False, due_date__lt=timezone.now()).exists():
        messages.error(request, "Vous avez des emprunts en retard. Impossible d'emprunter de nouveaux médias.")
        return redirect('staff:media_liste')

    # Vérifie si l'utilisateur a déjà 3 emprunts actifs
    if StaffBorrowItem.objects.filter(user=request.user, return_date__isnull=True).count() >= 3:
        messages.error(request, "Vous avez atteint la limite de 3 emprunts.")
        return redirect('staff:media_liste')

    # Calcule la date limite de retour
    due_date = timezone.now() + timezone.timedelta(days=7)

    # Utilise le formulaire d'emprunt
    if request.method == 'POST':
        form = BorrowMediaForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Crée l'objet d'emprunt
                borrow_item = StaffBorrowItem.objects.create(
                    user=request.user,
                    media=media,
                    borrow_date=timezone.now(),
                    due_date=due_date
                )
                # Marque le média comme non disponible
                media.is_available = False
                media.save()

            # Redirection vers la page de succès
            return redirect('staff:borrow_success', pk=borrow_item.pk)  # Passer l'identifiant de l'emprunt

    else:
        # Formulaire pré-rempli avec les informations du média
        form = BorrowMediaForm(initial={'media': media, 'due_date': due_date})

    # Retour  page de confirmation avec le formulaire
    return render(request, 'staff/media/borrow_confirm.html', {
        'form': form,
        'media': media,
        'due_date': due_date,
    })


# Succès de l'emprunt
def borrow_success(request, pk):
    # Récupére l'objet d'emprunt avec le pk
    borrow_item = get_object_or_404(StaffBorrowItem, pk=pk)
    media = borrow_item.media  # Récupére le média associé à l'emprunt

    return render(request, 'staff/media/borrow_success.html', {
        'borrow_item': borrow_item,
        'media': media,
    })


# Détail d'un emprunt
@permission_required('authentification.can_view_borrow', raise_exception=True)
def borrow_detail(request, pk):
    print(f"PK reçu : {pk}")  # Debug pour vérifier que pk est bien passé
    try:
        borrow_item = StaffBorrowItem.objects.get(pk=pk)
    except StaffBorrowItem.DoesNotExist:
        messages.error(request, "L'emprunt que vous cherchez n'existe pas.")
        return redirect('staff:media_liste')

    media = borrow_item.media
    user = borrow_item.user
    is_late = borrow_item.due_date < timezone.now() and not borrow_item.is_returned

    context = {
        'borrow_item': borrow_item,
        'media': media,
        'user': user,
        'is_late': is_late,
    }

    return render(request, 'staff/media/borrow_detail.html', context)


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

        return redirect('staff:borrow_detail', pk=borrow_item.pk)  # Rediriger vers la page des détails de l'emprunt

    # Si l'utilisateur tente d'accéder à cette vue sans soumettre le formulaire (GET request)
    messages.error(request, "Veuillez sélectionner un média à retourner.")
    return redirect('staff:borrow_detail', pk=borrow_item.pk)
