from django.shortcuts import render
from django.http import HttpResponseForbidden


def client_dashboard(request):
    if not request.user.is_client_user:
        return HttpResponseForbidden("Accès limité aux clients.")
    return render(request, 'authentification/client_dashboard.html')
