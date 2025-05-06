from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from staff.models import MediaStaff, StaffBorrowItem, BoardGameStaff
from staff.forms import MediaForm, BoardGameForm
from django.core.paginator import Paginator

MAX_BORROW_DURATION_DAYS = 7


@permission_required('authentification.can_add_media', raise_exception=True)
def add_media(request):
    if request.method == 'POST':
        media_form = MediaForm(request.POST)
        board_game_form = BoardGameForm(request.POST) if 'is_board_game' in request.POST else None

        if media_form.is_valid():
            is_board_game = media_form.cleaned_data.get('is_board_game')

            if is_board_game:
                if board_game_form and board_game_form.is_valid():
                    media = media_form.save()
                    board_game = board_game_form.save(commit=False)
                    board_game.media = media
                    board_game.save()
                    messages.success(request, "Le jeu de plateau a été ajouté avec succès.")
                    return redirect('staff:media_liste')
                else:
                    messages.error(request, "Il y a des erreurs dans le formulaire du jeu de plateau.")
            else:
                media_form.save()
                messages.success(request, "Le média a été ajouté avec succès.")
                return redirect('staff:media_liste')
    else:
        media_form = MediaForm()
        board_game_form = BoardGameForm()

    return render(request, 'staff/add_media.html', {
        'media_form': media_form,
        'board_game_form': board_game_form
    })


@permission_required('authentification.can_view_media', raise_exception=True)
def media_list(request):
    medias = MediaStaff.objects.all()
    paginator = Paginator(medias, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'staff/media_list.html', {'page_obj': page_obj})


@permission_required('authentification.can_view_media', raise_exception=True)
def media_detail(request, pk):
    media = get_object_or_404(MediaStaff, pk=pk)
    return render(request, 'staff/media_detail.html', {'media': media})


@permission_required('authentification.can_borrow_media', raise_exception=True)
def borrow_media(request, pk):
    media = get_object_or_404(MediaStaff, pk=pk)
    if not media.is_borrowable_by(request.user):
        messages.error(request, 'Ce média ne peut pas être emprunté.')
        return redirect('staff:media_liste')

    if not StaffBorrowItem.can_borrow(request.user):
        messages.error(request, 'Vous avez atteint la limite d\'emprunts ou vous avez des emprunts en retard.')
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

    return render(request, 'staff/borrow_detail.html', context)


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
