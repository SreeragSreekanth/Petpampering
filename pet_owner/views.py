# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import PetOwnerProfile, Pet, CommunityPost, Feedback
from .forms import PetOwnerProfileForm, PetForm, AppointmentForm, RescheduleAppointmentForm, CommunityPostForm,ReplyForm, FeedbackForm
from groom_interface.models import Appointment, Service
from django.contrib import messages
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from django.db.models import Q
from grooming_session_tracker.utils import send_notification
from grooming_session_tracker.models import Notification


@login_required
def profile_management(request):
    profile = request.user.pet_owner_profile
    if request.method == 'POST':
        form = PetOwnerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_management')
    else:
        form = PetOwnerProfileForm(instance=profile)
    return render(request, 'profile_management.html', {'form': form})

@login_required
def add_pet(request):
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = request.user
            pet.save()
            return redirect('pet_list')
    else:
        form = PetForm()
    return render(request, 'add_pet.html', {'form': form})

@login_required
def edit_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            return redirect('pet_list')
    else:
        form = PetForm(instance=pet)
    return render(request, 'edit_pet.html', {'form': form})

@login_required
def delete_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    pet.delete()
    return redirect('pet_list')

@login_required
def pet_list(request):
    pets = Pet.objects.filter(owner=request.user)
    return render(request, 'pet_list.html', {'pets': pets})

# views.py
@login_required
def dashboard(request):
    profile = PetOwnerProfile.objects.get_or_create(user=request.user)[0]
    pets = Pet.objects.filter(owner=request.user)
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    return render(request, 'dashboard.html', {
        'profile': profile,
        'pets': pets,
        'notifications': notifications
    })

@login_required
def browse_services(request):
    query = request.GET.get('q', '')  # Get search query from URL
    services = Service.objects.filter(availability=True)

    if query:
        # Combine multiple search conditions with Q objects
        services = services.filter(
            Q(name__icontains=query) | 
            Q(pet_type__icontains=query) | 
            Q(description__icontains=query) |  # Search within the description field as well
            Q(groomer__username__icontains=query)
        )

    # AI Recommendation Logic
    recommended_services = []
    if request.user.is_authenticated:
        pets = Pet.objects.filter(owner=request.user)  # Get user's pets

        if pets.exists():
            pet_types = [pet.pet_type.lower() for pet in pets]
            print("Pet Types:", pet_types)
            pet_weights = [float(pet.weight) for pet in pets]
            pet_ages = [pet.age for pet in pets]
            grooming_prefs = [pet.grooming_preferences.lower() for pet in pets if pet.grooming_preferences]

            # Debugging: Print available services and their pet_type
            available_services = Service.objects.filter(availability=True)
            print("Available Services:")
            for service in available_services:
                print(f"Service: {service.name}, Pet Type: {service.pet_type}")

            # Find services based on pet types only
            filtered_services = Service.objects.filter(
                availability=True,
                pet_type__in=[pet_type.lower() for pet_type in pet_types]  # Convert all pet types to lowercase
            )
            # Debugging: Check if any services match the filtered criteria
            print("Filtered Services:", filtered_services)

            # Check if no services are filtered and output details
            if not filtered_services:
                print("No services found for pet types:", pet_types)

            # AI-based filtering
            service_features = []
            service_map = {}

            for index, service in enumerate(filtered_services):
                pet_type_match = 1 if service.pet_type.lower() in pet_types else 0
                avg_weight = np.mean(pet_weights) if pet_weights else 0
                avg_age = np.mean(pet_ages) if pet_ages else 0
                grooming_pref_match = 1 if any(pref in service.description.lower() for pref in grooming_prefs) else 0

                feature_vector = [pet_type_match, avg_weight, avg_age, grooming_pref_match]
                service_features.append(feature_vector)
                service_map[index] = service

            if service_features:
                similarity_matrix = cosine_similarity([service_features[0]], service_features)
                recommended_indices = np.argsort(similarity_matrix[0])[::-1]
                recommended_services = [service_map[i] for i in recommended_indices[:5]]

            print("Recommended Services:", recommended_services)

    return render(request, "browse_services.html", {
        "services": services,
        "recommended_services": recommended_services,
        "query": query,
    })




@login_required
def book_appointment(request, service_id):
    service = get_object_or_404(Service, id=service_id)

    # Ensure that the logged-in user has a pet
    pet = Pet.objects.filter(owner=request.user).first()
    if not pet:
        return redirect('error_page')  # Redirect to error page if the user doesn't have a pet

    if request.method == 'POST':
        form = AppointmentForm(request.POST, user=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
            
            # Set the groomer (from the service) and pet_owner (from the logged-in user)
            appointment.groomer = service.groomer  # Set the groomer from the service
            appointment.pet_owner = request.user  # Set the pet owner to the logged-in user
            appointment.service = service  # Ensure the service is set
            
            # Set the pet for the appointment
            appointment.pet = pet  # Set the pet to the first pet owned by the logged-in user

            appointment.save()  # Save the appointment

            # Send notifications to both parties
            send_notification(
                user=appointment.pet_owner,
                message=f"Your appointment for {service.name} has been booked for {appointment.date_time.strftime('%Y-%m-%d %H:%M')}."
            )
            send_notification(
                user=appointment.groomer,
                message=f"A new appointment for {service.name} has been booked by {appointment.pet_owner.username} for {appointment.date_time.strftime('%Y-%m-%d %H:%M')}."
            )

            return redirect('view_appointments')  # Redirect to a success page or dashboard
    else:
        form = AppointmentForm(user=request.user)

    return render(request, 'book_appointment.html', {'form': form, 'service': service})

@login_required
def view_appointments(request):
    appointments = Appointment.objects.filter(pet_owner=request.user)
    return render(request, 'view_appointments.html', {'appointments': appointments})

@login_required
def reschedule_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Ensure that only the pet owner can reschedule
    if request.user != appointment.pet_owner:
        messages.error(request, "You are not authorized to reschedule this appointment.")
        return redirect('error_page')

    if request.method == 'POST':
        form = RescheduleAppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            appointment = form.save(commit=False)

            # Set status back to pending
            appointment.status = "pending"
            appointment.save()  # Save the rescheduled appointment

            # Create notification for groomer
            send_notification(
                user=appointment.pet_owner,
                message=f"Your appointment for {appointment.service.name} has been rescheduled to {appointment.date_time.strftime('%Y-%m-%d %H:%M')}."
            )
            send_notification(
                user=appointment.groomer,
                message=f"The appointment for {appointment.service.name} with {appointment.pet_owner.username} has been rescheduled to {appointment.date_time.strftime('%Y-%m-%d %H:%M')}."
            )

            messages.success(request, "Appointment rescheduled successfully.")
            return redirect('view_appointments')  # Redirect after rescheduling

    else:
        form = RescheduleAppointmentForm(instance=appointment)

    return render(request, 'reschedule_appointment.html', {'form': form, 'appointment': appointment})


@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, pet_owner=request.user)
    if request.method == 'POST':
        confirm_cancel = request.POST.get('confirm_cancel')
        if confirm_cancel:
            # Send notifications to both parties
            send_notification(
                user=appointment.pet_owner,
                message=f"Your appointment for {appointment.service.name} on {appointment.date_time.strftime('%Y-%m-%d %H:%M')} has been canceled."
            )
            send_notification(
                user=appointment.groomer,
                message=f"The appointment for {appointment.service.name} with {appointment.pet_owner.username} on {appointment.date_time.strftime('%Y-%m-%d %H:%M')} has been canceled."
            )

            appointment.delete()
            messages.success(request, 'Your appointment has been cancelled successfully.')
            return redirect('view_appointments')
    messages.info(request, 'Are you sure you want to cancel this appointment?')
    return redirect('view_appointments')


@login_required
def community_posts(request):
    posts = CommunityPost.objects.all().order_by('-created_at')
    return render(request, "community_posts.html", {"posts": posts})

@login_required
def create_community_post(request):
    if request.method == "POST":
        form = CommunityPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.owner = request.user
            post.save()
            return redirect('community_posts')
    else:
        form = CommunityPostForm()
    return render(request, "create_community_post.html", {"form": form})



@login_required
def view_community_post(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id)
    replies = post.replies.all().order_by("created_at")  # Fetch all replies

    if request.method == "POST":
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.post = post
            reply.save()
            return redirect('view_post', post_id=post.id)
    else:
        form = ReplyForm()

    return render(request, "view_community_post.html", {"post": post, "replies": replies, "form": form})


@login_required
def leave_feedback(request, service_id):
    service = get_object_or_404(Service, id=service_id)

    # Check if the user has already left feedback for this service
    if Feedback.objects.filter(service=service, pet_owner=request.user).exists():
        messages.error(request, "You have already left feedback for this service.")
        return redirect('view_service', service_id=service.id)

    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.pet_owner = request.user
            feedback.service = service
            feedback.save()
            messages.success(request, "Your feedback has been submitted.")
            return redirect('view_service', service_id=service.id)
    else:
        form = FeedbackForm()  # Ensure form is passed even for GET requests

    return render(request, "leave_feedback.html", {"service": service, "form": form})


@login_required
def edit_feedback(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)
    
    # Check if the user is the owner of the feedback or an admin
    if feedback.pet_owner != request.user and not request.user.is_staff:
        messages.error(request, "You are not authorized to edit this feedback.")
        return redirect('view_service', service_id=feedback.service.id)

    if request.method == "POST":
        form = FeedbackForm(request.POST, instance=feedback)
        if form.is_valid():
            form.save()
            messages.success(request, "Feedback updated successfully.")
            return redirect('view_service', service_id=feedback.service.id)
    else:
        form = FeedbackForm(instance=feedback)

    return render(request, 'edit_feedback.html', {'form': form, 'feedback': feedback})

# Delete Feedback
@login_required
def delete_feedback(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)
    
    # Check if the user is the owner of the feedback or an admin
    if feedback.pet_owner != request.user and not request.user.is_staff:
        messages.error(request, "You are not authorized to delete this feedback.")
        return redirect('view_service', service_id=feedback.service.id)

    feedback.delete()
    messages.success(request, "Feedback deleted successfully.")
    return redirect('view_service', service_id=feedback.service.id)