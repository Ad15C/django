from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from staff.models import MediaStaff, BoardGameStaff, StaffBorrowItem
from django.core.paginator import Paginator
from django.db import transaction

User = get_user_model()
MAX_BORROW_DURATION_DAYS = 7


# Formulaire pour les médias
class MediaForm(forms.ModelForm):
    is_board_game = forms.BooleanField(required=False, label="Est un jeu de plateau ?")

    class Meta:
        model = MediaStaff
        fields = ['name', 'media_type', 'available']


class BoardGameForm(forms.ModelForm):
    class Meta:
        model = BoardGameStaff
        fields = ['name', 'creators', 'is_visible', 'is_available', 'game_type']


# Ajouter un média
@permission_required('authentification.can_add_media', raise_exception=True)
def add_media(request):
    if request.method == 'POST':
        media_form = MediaForm(request.POST)
        board_game_form = None  # Initialise board_game_form à None

        if media_form.is_valid():
            media = media_form.save()

            if media_form.cleaned_data.get('is_board_game'):
                board_game_form = BoardGameForm(request.POST)
                if board_game_form.is_valid():
                    board_game = board_game_form.save(commit=False)
                    board_game.media = media
                    board_game.save()
                    messages.success(request, "Le jeu de plateau a été ajouté avec succès.")
                else:
                    messages.error(request, "Il y a des erreurs dans le formulaire du jeu de plateau.")

            messages.success(request, "Le média a été ajouté avec succès.")
            return redirect('media_list')
    else:
        media_form = MediaForm()
        board_game_form = BoardGameForm()

    return render(request, 'staff/add_media.html', {
        'media_form': media_form,
        'board_game_form': board_game_form or BoardGameForm()
        # Si pas de jeu de plateau, on utilise un formulaire vide.
    })


# Détail d'un média
@permission_required('authentification.can_view_media', raise_exception=True)
def media_detail(request, pk):
    media = get_object_or_404(MediaStaff, pk=pk)

    borrow = media.borrows.filter(is_returned=False).first()
    media_status = {
        'media': media,
        'is_borrowed': bool(borrow),
        'borrower': borrow.user if borrow else None,
        'borrow_date': borrow.borrow_date if borrow else None,
        'due_date': borrow.due_date if borrow else None
    }

    return render(request, 'staff/media_detail.html', {'media_status': media_status})


# Emprunter un média
@permission_required('authentification.can_borrow_media', raise_exception=True)
def borrow_media(request, pk):
    if request.method == 'POST':
        media = get_object_or_404(MediaStaff, pk=pk)

        # Vérifier si c'est un jeu de plateau et s'il peut être emprunté
        if not media.is_borrowable_by(request.user):
            messages.error(request, 'Ce média ne peut pas être emprunté.')
            return redirect('media_list')

        if not StaffBorrowItem.can_borrow(request.user):
            messages.error(request,
                           'Vous ne pouvez pas emprunter plus de 3 médias à la fois ou vous avez des emprunts en retard.')
            return redirect('media_list')

        due_date = timezone.now() + timezone.timedelta(days=MAX_BORROW_DURATION_DAYS)

        # Utilisation de la transaction pour garantir que les modifications sont atomiques
        with transaction.atomic():
            borrow_item = StaffBorrowItem.objects.create(  # Utilisation de borrow_item
                user=request.user,
                media=media,
                borrow_date=timezone.now(),
                due_date=due_date
            )

            # Mettre à jour l'état de la disponibilité du média dans la même transaction
            media.available = False
            media.save()

            # Utilisation de borrow_item si nécessaire (par exemple, pour des logs ou un message)
            # logging.info(f"Emprunt effectué pour {borrow_item.media.name} par {borrow_item.user}")

        messages.success(request,
                         f"Le média '{media.name}' a été emprunté avec succès. Vous devez le rendre avant le {due_date.date()}.")
        return redirect('media_list')

    return redirect('media_list')  # Retour explicite si POST n'est pas effectué


# Détail d'un emprunt
@permission_required('authentification.can_view_borrow', raise_exception=True)
def borrow_detail(request, pk):
    borrow = get_object_or_404(StaffBorrowItem, pk=pk)

    # Récupérer le média emprunté et l'utilisateur qui a emprunté
    media = borrow.media
    user = borrow.user

    # Calculer le statut de l'emprunt (retardé ou pas)
    is_late = borrow.due_date < timezone.now() and not borrow.is_returned

    context = {
        'borrow': borrow,
        'media': media,
        'user': user,
        'is_late': is_late,
    }

    return render(request, 'staff/borrow_detail.html', context)


# Retourner un média
@permission_required('authentification.can_return_media', raise_exception=True)
def return_media(request, pk):
    if request.method == 'POST':
        borrow = get_object_or_404(StaffBorrowItem, pk=pk, is_returned=False)
        borrow.is_returned = True
        borrow.return_date = timezone.now()
        borrow.save()
        borrow.media.available = True
        borrow.media.save()

        messages.success(request, "Le média a été retourné avec succès.")
        return redirect('media_list')

    return redirect('media_list')  # Retour explicite


# Liste des médias avec filtres
@permission_required('authentification.can_view_media', raise_exception=True)
def media_list(request):
    media_type_filter = request.GET.get('media_type', None)
    available_filter = request.GET.get('available', None)

    medias = MediaStaff.objects.all()

    if media_type_filter:
        medias = medias.filter(media_type=media_type_filter)

    if available_filter is not None:
        available_filter = available_filter.lower() == 'true'
        medias = medias.filter(available=available_filter)

    paginator = Paginator(medias, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    media_status = []
    for media in page_obj:
        borrow = media.borrows.filter(is_returned=False).first()
        media_status.append({
            'media': media,
            'is_borrowed': bool(borrow),
            'borrower': borrow.user if borrow else None,
            'borrow_date': borrow.borrow_date if borrow else None,
            'due_date': borrow.due_date if borrow else None
        })

    return render(request, 'staff/media_list.html', {
        'media_status': media_status,
        'media_type_filter': media_type_filter,
        'available_filter': available_filter,
        'page_obj': page_obj
    })
