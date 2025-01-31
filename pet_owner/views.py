# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import PetOwnerProfile, Pet
from .forms import PetOwnerProfileForm, PetForm

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
    return render(request, 'dashboard.html', {'profile': profile, 'pets': pets})