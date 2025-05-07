from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from staff.models import MediaStaff, StaffBorrowItem, BoardGameStaff, BookStaff, DVDStaff, CDStaff
from staff.forms import MediaForm, BoardGameForm, BookForm, CDForm, DVDForm
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden

MAX_BORROW_DURATION_DAYS = 7


def staff_dashboard(request):
    if not request.user.is_staff_user:
        return HttpResponseForbidden("Vous n'êtes pas autorisé à voir cette page.")
    return render(request, 'authentification/staff_dashboard.html')


@permission_required('authentification.can_add_media', raise_exception=True)
def add_media(request):
    if request.method == 'POST':
        # Initialisation du formulaire de base pour le média
        media_form = MediaForm(request.POST)

        # Initialisation conditionnelle des formulaires spécifiques
        board_game_form = BoardGameForm(request.POST) if 'is_board_game' in request.POST else None
        book_form = BookForm(request.POST) if 'is_book' in request.POST else None
        dvd_form = DVDForm(request.POST) if 'is_dvd' in request.POST else None
        cd_form = CDForm(request.POST) if 'is_cd' in request.POST else None

        if media_form.is_valid():
            # Sauvegarder le média de base (common fields)
            media = media_form.save()

            # Sauvegarder un jeu de société si sélectionné
            if 'is_board_game' in request.POST and board_game_form and board_game_form.is_valid():
                board_game = board_game_form.save(commit=False)
                board_game.media = media
                board_game.save()

            # Sauvegarder un livre si sélectionné
            if 'is_book' in request.POST and book_form and book_form.is_valid():
                book = book_form.save(commit=False)
                book.media = media
                book.save()

            # Sauvegarder un DVD si sélectionné
            if 'is_dvd' in request.POST and dvd_form and dvd_form.is_valid():
                dvd = dvd_form.save(commit=False)
                dvd.media = media
                dvd.save()

            # Sauvegarder un CD si sélectionné
            if 'is_cd' in request.POST and cd_form and cd_form.is_valid():
                cd = cd_form.save(commit=False)
                cd.media = media
                cd.save()

            messages.success(request, "Le média a été ajouté avec succès.")
            return redirect('staff:media_liste')

    else:
        # Initialisation des formulaires vides
        media_form = MediaForm()
        board_game_form = BoardGameForm()
        book_form = BookForm()
        dvd_form = DVDForm()
        cd_form = CDForm()

    return render(request, 'staff/media/add_media.html', {
        'media_form': media_form,
        'board_game_form': board_game_form,
        'book_form': book_form,
        'dvd_form': dvd_form,
        'cd_form': cd_form,
    })


@permission_required('authentification.can_view_media', raise_exception=True)
def media_list(request):
    available_filter = request.GET.get('available', None)

    # Traitement du filtre
    if available_filter == "true":
        media_items = MediaStaff.objects.filter(is_available=True)
    elif available_filter == "false":
        media_items = MediaStaff.objects.filter(is_available=False)
    else:
        media_items = MediaStaff.objects.all()  # Si aucun filtre, tous les éléments

    # Récupérer d'autres filtres si nécessaire, par exemple media_type, only_borrowable
    media_type_filter = request.GET.get('media_type', '')
    if media_type_filter:
        media_items = media_items.filter(media_type__icontains=media_type_filter)

    # Paginator si nécessaire (pour pagination)
    from django.core.paginator import Paginator
    paginator = Paginator(media_items, 10)  # 10 par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'media_type_filter': media_type_filter,
        'available_filter': available_filter,
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

    # Vérifier si c'est un jeu de société
    if isinstance(media, BoardGameStaff):
        messages.error(request, "Les jeux de société ne peuvent pas être empruntés.")
        return redirect('staff:media_liste')

    # Vérifier si l'utilisateur peut emprunter ce média (règle des 3 emprunts et des retards)
    if not StaffBorrowItem.can_borrow(request.user):
        messages.error(request, 'Vous avez atteint la limite d\'emprunts ou vous avez des emprunts en retard.')
        return redirect('staff:media_liste')

    # Vérifier si le média peut être emprunté
    if not media.is_borrowable_by(request.user):
        messages.error(request, 'Ce média ne peut pas être emprunté.')
        return redirect('staff:media_liste')

    due_date = timezone.now() + timezone.timedelta(days=MAX_BORROW_DURATION_DAYS)
    with transaction.atomic():
        borrow_item = StaffBorrowItem.objects.create(
            user=request.user, media=media, borrow_date=timezone.now(), due_date=due_date
        )
        media.available = False
        media.save()

    messages.success(request, f"Vous avez emprunté le média '{media.name}', retour prévu avant le {due_date.date()}.")
    return redirect('staff:media_liste')


# Détail d'un emprunt
@permission_required('authentification.can_view_borrow', raise_exception=True)
def borrow_detail(request, pk):
    borrow_item = get_object_or_404(StaffBorrowItem, pk=pk)

    # Récupérer le média emprunté et l'utilisateur qui a emprunté
    media = borrow_item.media
    user = borrow_item.user

    # Calculer le statut de l'emprunt (retardé ou pas)
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
    borrow_item = get_object_or_404(StaffBorrowItem, pk=pk, is_returned=False)

    # Si le média est déjà retourné
    if borrow_item.is_returned:
        messages.error(request, "Ce média a déjà été retourné.")
        return redirect('staff:media_liste')

    borrow_item.is_returned = True
    borrow_item.return_date = timezone.now()
    borrow_item.save()

    # Rendre le média disponible à nouveau
    borrow_item.media.is_available = True
    borrow_item.media.save()

    messages.success(request, "Le média a été retourné avec succès.")
    return redirect('staff:media_liste')
