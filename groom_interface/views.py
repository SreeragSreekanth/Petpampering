import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import GroomerProfile, Service, Appointment
from .forms import GroomerProfileForm, ServiceForm
from django.contrib import messages
from userauth.models import User
from pet_owner.models import Feedback 
from .forms import ResponseForm
from grooming_session_tracker.utils import send_notification
from grooming_session_tracker.models import Notification,Invoice,Payment
from userauth.decorators import role_required



@login_required
@role_required(['groomer'])
def groomer_dashboard(request):
    # Fetch the groomer's profile
    profile = get_object_or_404(GroomerProfile, user=request.user)
    
    # Fetch services offered by the groomer
    services = Service.objects.filter(groomer=request.user)

    # Fetch unread notifications
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')

    # Fetch appointment counts (replace with your actual model logic)
    upcoming_appointments = Appointment.objects.filter(groomer=request.user, status='upcoming').count()
    pending_appointments = Appointment.objects.filter(groomer=request.user, status='pending').count()

    # Mark notifications as read if requested
    if request.GET.get('mark_as_read'):
        notifications.update(is_read=True)
        return redirect('groomer_dashboard')  # Redirect to refresh the page

    # Render the dashboard with profile, services, and notifications
    return render(request, 'groomer.html', {
        'profile': profile,
        'services': services,
        'notifications': notifications,
        'upcoming_appointments': upcoming_appointments,
        'pending_appointments': pending_appointments,
    })

@role_required(['groomer','admin'])
def groomer_profile(request, groomer_id):
    groomer = get_object_or_404(User, id=groomer_id, role='groomer')  
    groomer_profile = get_object_or_404(GroomerProfile, user=groomer)  # Fetch Groomer's profile
    services = Service.objects.filter(groomer=groomer)  # Fetch services offered by the groomer

    return render(request, 'groomer_profile.html', {
        'groomer': groomer,
        'groomer_profile': groomer_profile,
        'services': services
    })

@login_required
@role_required(['groomer'])
def edit_profile(request):
    profile = get_object_or_404(GroomerProfile, user=request.user)
    if request.method == 'POST':
        form = GroomerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('groomer_dashboard')
    else:
        form = GroomerProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})

@login_required
@role_required(['groomer'])
def manage_services(request):
    services = Service.objects.filter(groomer=request.user)
    return render(request, 'manage_services.html', {'services': services})

@login_required
@role_required(['groomer'])
def add_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)  # Include request.FILES to handle image uploads
        if form.is_valid():
            service = form.save(commit=False)
            service.groomer = request.user  # Set the groomer to the currently logged-in user
            service.save()
            return redirect('manage_services')  # Redirect to manage services after saving
    else:
        form = ServiceForm()  # Initialize the form if the request is GET

    return render(request, 'add_service.html', {'form': form})

@login_required
@role_required(['groomer'])
def edit_service(request, service_id):
    # Get the service that matches the ID and belongs to the current groomer
    service = get_object_or_404(Service, id=service_id, groomer=request.user)

    # Handle POST request to update the service
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, "The service has been updated successfully.")
            return redirect('manage_services')
    else:
        form = ServiceForm(instance=service)

    return render(request, 'edit_service.html', {'form': form})

@login_required
def delete_service(request, service_id):
    # Retrieve the service using the service_id and ensure the logged-in user is the groomer
    service = get_object_or_404(Service, id=service_id, groomer=request.user)

    # Check if the service has an associated image and delete it
    if service.image:
        # Delete the image file from the storage
        if os.path.exists(service.image.path):
            os.remove(service.image.path)

    # Delete the service itself
    service.delete()

    # Success message
    
    # Redirect to the manage services page after deletion
    return redirect('manage_services')

@login_required
def view_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    
    # Check if the user has already left feedback for this service
    has_left_feedback = Feedback.objects.filter(service=service, pet_owner=request.user).exists()

    return render(request, 'view_service.html', {
        'service': service,
        'has_left_feedback': has_left_feedback,
    })


@login_required
@role_required(['groomer'])
def manage_appointments(request):
    appointments = Appointment.objects.filter(groomer=request.user).order_by('-date_time')
    return render(request, 'manage_appointments.html', {'appointments': appointments})



@login_required
@role_required(['groomer'])
def update_appointment_status(request, appointment_id, status):
    appointment = get_object_or_404(Appointment, id=appointment_id, groomer=request.user)
    if status in ["accepted", "declined"]:
        appointment.status = status
        appointment.save()
        messages.success(request, f"Appointment has been {status}.")
        # Send notifications
        send_notification(
            user=appointment.pet_owner,
            message=f"Your appointment for {appointment.service.name} has been {status}."
        )
    else:
        messages.error(request, "Invalid status update.")
    return redirect('manage_appointments')


# views.py (groom_interface/views.py)
@login_required
@role_required(['groomer'])
def respond_to_feedback(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)
    # Ensure the logged-in user is the groomer of the service
    if feedback.service.groomer != request.user:
        messages.error(request, "You are not authorized to respond to this feedback.")
        return redirect('view_service', service_id=feedback.service.id)
    # Check if a response already exists
    if hasattr(feedback, 'response'):
        messages.error(request, "You have already responded to this feedback.")
        return redirect('view_service', service_id=feedback.service.id)
    if request.method == "POST":
        form = ResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.feedback = feedback
            response.groomer = request.user
            response.save()
            messages.success(request, "Your response has been submitted.")
            # Send notification to the pet owner
            send_notification(
                user=feedback.pet_owner,
                message=f"The groomer has responded to your feedback for {feedback.service.name}."
            )
            return redirect('view_service', service_id=feedback.service.id)
    else:
        form = ResponseForm()  # Ensure form is passed even for GET requests
    return render(request, "respond_to_feedback.html", {"form": form, "feedback": feedback})