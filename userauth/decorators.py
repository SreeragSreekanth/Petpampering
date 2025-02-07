# userauth/decorators.py
from functools import wraps
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

def role_required(allowed_roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                raise PermissionDenied  # Deny access if the role is not allowed
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def superuser_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return redirect('/login/')  # Redirect to login page or custom URL
        return view_func(request, *args, **kwargs)
    return wrapper