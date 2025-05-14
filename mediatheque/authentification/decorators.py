from django.http import HttpResponseForbidden
from functools import wraps


def role_required(required_role):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role != required_role:
                return HttpResponseForbidden("Accès refusé : rôle inadapté.")
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
