import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import GroomerProfile, Service, Appointment
from .forms import GroomerProfileForm, ServiceForm
from django.contrib import messages


@login_required
def groomer_dashboard(request):
    profile = get_object_or_404(GroomerProfile, user=request.user)
    services = Service.objects.filter(groomer=request.user)
    return render(request, 'groomer.html', {'profile': profile, 'services': services})

@login_required
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
def manage_services(request):
    services = Service.objects.filter(groomer=request.user)
    return render(request, 'manage_services.html', {'services': services})

@login_required
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
    # Retrieve the service based on the service_id
    service = get_object_or_404(Service, id=service_id)

    # Render the service details page
    return render(request, 'view_service.html', {'service': service})

@login_required
def manage_appointments(request):
    appointments = Appointment.objects.filter(groomer=request.user).order_by('-date_time')
    return render(request, 'manage_appointments.html', {'appointments': appointments})

@login_required
def update_appointment_status(request, appointment_id, status):
    appointment = get_object_or_404(Appointment, id=appointment_id, groomer=request.user)
    
    if status in ["accepted", "declined"]:
        appointment.status = status
        appointment.save()
        messages.success(request, f"Appointment has been {status}.")
    else:
        messages.error(request, "Invalid status update.")

    return redirect('manage_appointments')
