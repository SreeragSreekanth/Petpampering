from django.shortcuts import render,redirect,get_object_or_404
from .models import Notification  # Assuming you have a Notification model
from django.contrib.auth.decorators import login_required


# Notifications
@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notifications})

# Mark Notification as Read
@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications')  # Redirect back to the notifications page

# Mark All Notifications as Read
@login_required
def mark_all_as_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('notifications') 
