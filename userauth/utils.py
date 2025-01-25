from .models import User

def clear_approval_for_superuser(user):
    """Clear the approval status for superusers."""
    if user.is_superuser:
        user.is_approved = True
        user.save()
