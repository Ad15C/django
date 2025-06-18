from django.http import HttpResponseForbidden
from functools import wraps


def role_required(*roles):
    """
    Autorise uniquement les utilisateurs appartenant aux groupes donnés dans roles.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Utilisateur non authentifié.")
            if str(request.user.role) not in [str(role) for role in roles]:
                return HttpResponseForbidden("Accès limité aux utilisateurs autorisés.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
