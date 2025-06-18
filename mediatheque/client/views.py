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

    borrows = ClientBorrow.objects.filter(user=user)
    available_media = MediaClient.objects.filter(is_available=True, can_borrow=True)

    context = {
        "user": user,
        "borrows": borrows,
        "available_media": available_media,
        "message": "Vous n'avez aucun emprunt en cours." if not borrows.exists() else None,
    }

    return render(request, "client/client_dashboard.html", context)
    pass
