# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('ownerdashboard/', views.dashboard, name='owner_dashboard'),
    path('profile/', views.profile_management, name='profile_management'),
    path('pets/', views.pet_list, name='pet_list'),
    path('pets/add/', views.add_pet, name='add_pet'),
    path('pets/edit/<int:pet_id>/', views.edit_pet, name='edit_pet'),
    path('pets/delete/<int:pet_id>/', views.delete_pet, name='delete_pet'),
]