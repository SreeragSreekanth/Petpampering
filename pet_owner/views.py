# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import PetOwnerProfile, Pet, CommunityPost, Feedback,PetBreed,PetType
from .forms import PetOwnerProfileForm, PetForm, AppointmentForm, RescheduleAppointmentForm, CommunityPostForm,ReplyForm, FeedbackForm
from groom_interface.models import Appointment, Service
from django.contrib import messages
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from django.db.models import Q
from grooming_session_tracker.utils import send_notification
from grooming_session_tracker.models import Notification, Invoice, Payment
from django.utils import timezone
from userauth.decorators import role_required
from django.http import HttpResponseForbidden
from .models import Reply
from django.db.models.functions import Lower
from userauth.models import User
from django.http import JsonResponse




def get_breeds(request):
    pet_type_id = request.GET.get('pet_type_id')
    breeds = PetBreed.objects.filter(pet_type_id=pet_type_id).values('id', 'name')
    return JsonResponse(list(breeds), safe=False)

@login_required
@role_required(['owner'])
def profile_management(request):
    profile = request.user.pet_owner_profile
    if request.method == 'POST':
        form = PetOwnerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('owner_dashboard')
    else:
        form = PetOwnerProfileForm(instance=profile)
    return render(request, 'profile_management.html', {'form': form})

@login_required
def add_pet(request):
    if request.method == "POST":
        form = PetForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = request.user  # Assign the current user as the pet owner
            pet.save()
            return redirect('pet_list')  # Redirect to pet list or details page
    else:
        form = PetForm()
    return render(request, 'add_pet.html', {'form': form})

@login_required
def edit_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)  # Ensure the user owns the pet
    if request.method == "POST":
        form = PetForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            return redirect('pet_list')  # Redirect to pet details page
    else:
        form = PetForm(instance=pet)
    return render(request, 'edit_pet.html', {'form': form, 'pet': pet})

@login_required
@role_required(['owner'])
def delete_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    pet.delete()
    return redirect('pet_list')

@login_required
@role_required(['owner'])
def pet_list(request):
    pets = Pet.objects.filter(owner=request.user)
    return render(request, 'pet_list.html', {'pets': pets})

# views.py
@login_required
@role_required(['owner'])
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
@role_required(['owner'])
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
            pet_weights = [float(pet.weight) for pet in pets]
            pet_ages = [pet.age for pet in pets]
            grooming_prefs = [pet.grooming_preferences.lower() for pet in pets if pet.grooming_preferences]
            
            # Filter services based on pet types (case-insensitive)
            filtered_services = Service.objects.annotate(
                lower_pet_type=Lower('pet_type')
            ).filter(
                availability=True,
                lower_pet_type__in=pet_types
            )
            
            # Debugging: Print available services and their pet_type
            available_services = Service.objects.filter(availability=True)
            print("Available Services:")
            for service in available_services:
                print(f"Service: {service.name}, Pet Type: {service.pet_type}")
            
            # If no services match the pet types, fallback to common pet types
            if not filtered_services.exists():
                print("No services found for pet types:", pet_types)
                filtered_services = Service.objects.filter(availability=True, pet_type__in=['dog', 'cat'])
            
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
                recommended_indices = np.argsort(similarity_matrix[0])[::-1]  # Sort by similarity score
                recommended_services = [service_map[i] for i in recommended_indices[:5]]  # Top 5 recommendations
            
            print("Recommended Services:", recommended_services)
    
    return render(request, "browse_services.html", {
        "services": services,
        "recommended_services": recommended_services,
        "query": query,
    })

@login_required
@role_required(['owner'])
def book_appointment(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    pet = Pet.objects.filter(owner=request.user).first()
    if not pet:
        return redirect('error_page')

    if request.method == 'POST':
        form = AppointmentForm(request.POST, user=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.groomer = service.groomer
            appointment.pet_owner = request.user
            appointment.service = service
            appointment.pet = pet
            appointment.save()

            # ✅ Create an Invoice for this appointment
            Invoice.objects.create(
                appointment=appointment,
                total_amount=service.price,  # Use 'total_amount' if your model has it
                status='pending'
            )


            # Send notifications
            send_notification(user=appointment.groomer, message=f"A new appointment has been booked.")
            send_notification(user=appointment.pet_owner, message=f"Your appointment has been booked.")

            return redirect('view_appointments')

    else:
        form = AppointmentForm(user=request.user)
    return render(request, 'book_appointment.html', {'form': form, 'service': service})

@login_required
@role_required(['owner'])
def view_appointments(request):
    appointments = Appointment.objects.filter(pet_owner=request.user)
    return render(request, 'view_appointments.html', {'appointments': appointments})

# views.py (pet_owner/views.py)
@login_required
@role_required(['owner'])
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
            # Send notifications
            send_notification(
                user=appointment.groomer,
                message=f"Appointment for {appointment.service.name} has been rescheduled to {appointment.date_time.strftime('%Y-%m-%d %H:%M')}. Please review."
            )
            send_notification(
                user=appointment.pet_owner,
                message=f"Your appointment for {appointment.service.name} has been rescheduled to {appointment.date_time.strftime('%Y-%m-%d %H:%M')}."
            )
            messages.success(request, "Appointment rescheduled successfully.")
            return redirect('view_appointments')
    else:
        form = RescheduleAppointmentForm(instance=appointment)
    return render(request, 'reschedule_appointment.html', {'form': form, 'appointment': appointment})


# views.py (pet_owner/views.py)
@login_required
@role_required(['owner'])
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, pet_owner=request.user)
    if request.method == 'POST':
        confirm_cancel = request.POST.get('confirm_cancel')  # Get the confirmation field
        if confirm_cancel:  # If confirmed, delete the appointment
            appointment.delete()
            messages.success(request, 'Your appointment has been cancelled successfully.')
            # Send notifications
            send_notification(
                user=appointment.groomer,
                message=f"Appointment for {appointment.service.name} on {appointment.date_time.strftime('%Y-%m-%d %H:%M')} has been cancelled."
            )
            send_notification(
                user=appointment.pet_owner,
                message=f"Your appointment for {appointment.service.name} on {appointment.date_time.strftime('%Y-%m-%d %H:%M')} has been cancelled."
            )
            return redirect('view_appointments')
    # If the form is not submitted, just render the appointments page with a confirmation message
    messages.info(request, 'Are you sure you want to cancel this appointment?')
    return redirect('view_appointments')


@login_required
@role_required(['owner'])
def community_posts(request):
    posts = CommunityPost.objects.all().order_by('-created_at')
    return render(request, "community_posts.html", {"posts": posts})

@login_required
@role_required(['owner'])
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
@role_required(['owner'])
def edit_community_post(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id)

    if post.owner != request.user:
        return HttpResponseForbidden("You are not allowed to edit this post.")

    if request.method == "POST":
        form = CommunityPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect("community_posts")
    else:
        form = CommunityPostForm(instance=post)

    return render(request, "edit_community_post.html", {"form": form, "post": post})


@login_required
@role_required(['owner'])
def delete_community_post(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id)

    if post.owner != request.user:
        return HttpResponseForbidden("You are not allowed to delete this post.")

    post.delete()
    return redirect("community_posts")


@login_required
@role_required(['owner'])
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


# views.py (pet_owner/views.py)
@login_required
@role_required(['owner'])
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
            # Send notification to the groomer
            send_notification(
                user=service.groomer,
                message=f"New feedback on your service {service.name}: {feedback.comment[:50]}..."
            )
            return redirect('view_service', service_id=service.id)
    else:
        form = FeedbackForm()  # Ensure form is passed even for GET requests
    return render(request, "leave_feedback.html", {"service": service, "form": form})


@login_required
@role_required(['owner'])
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
@role_required(['owner'])
def delete_feedback(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)
    
    # Check if the user is the owner of the feedback or an admin
    if feedback.pet_owner != request.user and not request.user.is_staff:
        messages.error(request, "You are not authorized to delete this feedback.")
        return redirect('view_service', service_id=feedback.service.id)

    feedback.delete()
    messages.success(request, "Feedback deleted successfully.")
    return redirect('view_service', service_id=feedback.service.id)


@login_required
def edit_reply(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)

    # Ensure only the owner can edit
    if reply.user != request.user:
        return HttpResponseForbidden("You are not allowed to edit this reply.")

    if request.method == "POST":
        form = ReplyForm(request.POST, instance=reply)
        if form.is_valid():
            form.save()
            return redirect('view_post', post_id=reply.post.id)
    else:
        form = ReplyForm(instance=reply)

    return render(request, "edit_reply.html", {"form": form, "reply": reply})

@login_required
def delete_reply(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)

    # Ensure only the owner can delete
    if reply.user != request.user:
        return HttpResponseForbidden("You are not allowed to delete this reply.")

    post_id = reply.post.id
    reply.delete()
    messages.success(request, "Reply deleted successfully.")

    return redirect('view_post', post_id=post_id)


@login_required
@role_required(['pet_owner','admin'])
def view_pet_owner(request, user_id):
    owner = get_object_or_404(User, id=user_id)
    owner_profile = get_object_or_404(PetOwnerProfile, user=owner)

    # Fetch pets owned by this pet owner
    pets = Pet.objects.filter(owner=owner)

    return render(request, 'view_pet_owner.html', {'owner': owner, 'pets': pets,'ownerprofile':owner_profile})

