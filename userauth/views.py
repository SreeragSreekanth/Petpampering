from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, LoginForm
from django.contrib import messages
from .utils import clear_approval_for_superuser  # Import the function to clear approval for superuser




# Define a function called signup_view that takes in a request as an argument
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login page after signup
        else:
            print(form.errors)  # Debugging: Print errors in console
    else:
        form = SignupForm()
    
    return render(request, 'signup.html', {'form': form})





def login_view(request):
    """Login View for existing users."""
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # If the user is a superuser and not approved, update their approval status
                if user.is_superuser and not user.is_approved:
                    user.is_approved = True  # Set user as approved
                    user.role = 'admin'  # Set user role as admin
                    user.save()  # Save the changes to the database

                # Check if the user is approved
                if user.is_approved:
                    login(request, user)

                    # Redirect based on user role
                    if user.is_superuser:
                        return redirect('admindash')  # Redirect to the admin dashboard
                    elif user.role == 'owner':  # Assuming role field exists in the User model
                        return redirect('owner_dashboard')  # Redirect to pet owner's dashboard
                    elif user.role == 'groomer':
                        return redirect('groomer_dashboard')  # Redirect to groomer's dashboard
                    else:
                        return redirect('home')  # Default redirect for users with no role
                else:
                    form.add_error(None, "Invalid credentials or account not approved.")
            else:
                form.add_error(None, "Invalid credentials or account not approved.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})



def logout_view(request):
    """Logout View to log out a user."""
    logout(request)
    return redirect('login')  # Redirect to login page after logging out



def home_view(request):
    """Home View after successful login."""
    return render(request, 'home.html', {'user': request.user})  # Render user info in home page



