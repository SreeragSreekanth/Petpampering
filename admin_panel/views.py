# admin_panel/views.py
from django.shortcuts import render, redirect, get_object_or_404
from userauth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from groom_interface.models import *
from groom_interface.forms import *
from django.contrib import messages
from userauth.decorators import  superuser_required
from pet_owner.models import PetType,PetBreed
from .forms import PetTypeForm,BreedForm


@login_required
@superuser_required
def manage_users(request):
    if not request.user.is_superuser:  # Check if the user is admin
        return redirect('home') 
    users = User.objects.filter(is_approved=True,role__in=['owner', 'groomer'])
    return render(request, 'manage_user/manage_users.html', {'users': users})

@login_required
@superuser_required

def admindash(request):
    return render(request,"admin.html")

@login_required
@superuser_required
def pending_users(request):
    """View all users awaiting approval."""
    if not request.user.is_superuser:
        return redirect('home')

    pending_users = User.objects.filter(is_approved=False)  # Get pending users
    return render(request, 'manage_user/pending_users.html', {'pending_users': pending_users})

@login_required
@superuser_required
def approve_user(request, user_id):
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)

        # Get the selected role from the form
        selected_role = request.POST.get("role")

        if selected_role in ["owner", "groomer", "admin"]:
            user.role = selected_role  # Update the user's role
            user.is_approved = True  # Mark user as approved
            user.save()  # Save changes

            messages.success(request, f"User {user.username} approved as {selected_role.capitalize()}.")
        else:
            messages.error(request, "Invalid role selected.")

    return redirect("pending_users")  # Redirect back to pending approvals


@login_required
@superuser_required
def delete_user(request, user_id):
    """Delete a user from the system."""
    if not request.user.is_superuser:
        return redirect('home')

    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, f"{user.username} has been deleted!")
    return redirect('manage_users')  # Redirect back to manage users page


@login_required
@superuser_required
def reject_user(request, user_id):
    """Reject a user by deleting the account."""
    user = get_object_or_404(User, id=user_id)
    if request.user.is_superuser:  # Only admins can reject
        user.delete()
        messages.error(request, f"User {user.username} has been rejected and deleted.")
    return redirect('manage_users')



@login_required
@superuser_required
def all_services(request):
    """ Display all grooming services with groomer details. """
    services = Service.objects.select_related('groomer').all()
    return render(request, 'manage_groomers/all_services.html', {'services': services})


@login_required
def delete_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    service.delete()
    messages.success(request, f"Service '{service.name}' has been deleted.")
    return redirect("all_services")



def pet_type_list(request):
    pet_types = PetType.objects.all()
    return render(request, "pet_type_list.html", {"pet_types": pet_types})

def pet_type_create(request):
    if request.method == "POST":
        form = PetTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Pet Type added successfully!")
            return redirect("pet_type_list")
    else:
        form = PetTypeForm()
    return render(request, "pet_type_form.html", {"form": form})

def pet_type_update(request, pk):
    pet_type = get_object_or_404(PetType, pk=pk)
    if request.method == "POST":
        form = PetTypeForm(request.POST, instance=pet_type)
        if form.is_valid():
            form.save()
            messages.success(request, "Pet Type updated successfully!")
            return redirect("pet_type_list")
    else:
        form = PetTypeForm(instance=pet_type)
    return render(request, "pet_type_form.html", {"form": form})

def pet_type_delete(request, pk):
    pet_type = get_object_or_404(PetType, pk=pk)
    pet_type.delete()
    messages.success(request, "Pet Type deleted successfully!")
    return redirect("pet_type_list")

# ---------- BREED CRUD -----------
def breed_list(request):
    breeds = PetBreed.objects.select_related("pet_type").all()
    return render(request, "breed_list.html", {"breeds": breeds})

def breed_create(request):
    if request.method == "POST":
        form = BreedForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Breed added successfully!")
            return redirect("breed_list")
    else:
        form = BreedForm()
    return render(request, "add_breed.html", {"form": form})

def breed_update(request, pk):
    breed = get_object_or_404(PetBreed, pk=pk)
    if request.method == "POST":
        form = BreedForm(request.POST, instance=breed)
        if form.is_valid():
            form.save()
            messages.success(request, "Breed updated successfully!")
            return redirect("breed_list")
    else:
        form = BreedForm(instance=breed)
    return render(request, "add_breed.html", {"form": form})

def breed_delete(request, pk):
    breed = get_object_or_404(PetBreed, pk=pk)
    breed.delete()
    messages.success(request, "Breed deleted successfully!")
    return redirect("breed_list")
        
