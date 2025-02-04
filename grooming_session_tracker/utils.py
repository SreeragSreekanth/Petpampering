from .models import Notification

def send_notification(user, message):
    """
    Sends a notification to the specified user.
    """
    Notification.objects.create(user=user, message=message)