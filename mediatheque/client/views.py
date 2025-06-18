from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from mediatheque.client.models import ClientBorrow, MediaClient
from django.http import HttpResponseForbidden
from mediatheque.authentification.decorators import role_required


def is_client(user):
    return user.groups.filter(name='client').exists()


@login_required
@role_required("client")
def client_dashboard(request):
    user = request.user

    borrows = ClientBorrow.objects.filter(user=user, returned=False)
    borrowed_media_ids = borrows.values_list('media_id', flat=True)

    available_media = MediaClient.objects.filter(is_available=True).exclude(media_type='board_game')

    # Ajouter détails et statut emprunté
    for media in available_media:
        # Détail auteur/producteur/...
        if media.media_type == 'book' and hasattr(media, 'bookclient'):
            media.details = f"Auteur : {media.bookclient.author}"
        elif media.media_type == 'dvd' and hasattr(media, 'dvdclient'):
            media.details = f"Producteur : {media.dvdclient.producer}"
        elif media.media_type == 'cd' and hasattr(media, 'cdclient'):
            media.details = f"Artiste : {media.cdclient.artist}"
        elif media.media_type == 'board_game' and hasattr(media, 'boardgameclient'):
            media.details = f"Créateur(s) : {media.boardgameclient.creators}"
        else:
            media.details = ""

        # Est-ce emprunté ?
        media.is_borrowed = media.id in borrowed_media_ids

    context = {
        "user": user,
        "borrows": borrows,
        "available_media": available_media,
        "message": "Vous n\'avez aucun emprunt en cours." if not borrows.exists() else None,
    }

    return render(request, "client/client_dashboard.html", context)
