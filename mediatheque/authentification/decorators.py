from django.http import HttpResponseForbidden
from functools import wraps


def role_required(role):
    """
    A decorator to check if the user has the specified role.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.role == role:
                return HttpResponseForbidden("Access Denied")
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
