from django.urls import path
from . import views

urlpatterns = [
    path('manage_users/', views.manage_users, name='manage_users'),
    path('admindash/',views.admindash,name="admindash"),
    path('pending_users/', views.pending_users, name='pending_users'),
    path('approve_user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('reject-user/<int:user_id>/', views.reject_user, name='reject_user'),
    path('assign_role/<int:user_id>/', views.reject_user, name='change_user_role'),
    path('manage_services/', views.all_services, name='all_services'),
    path('services/delete/<int:service_id>/', views.delete_service, name='delete_service'),
    path("pet-types/", views.pet_type_list, name="pet_type_list"),
    path("pet-types/add/", views.pet_type_create, name="pet_type_create"),
    path("pet-types/edit/<int:pk>/", views.pet_type_update, name="pet_type_update"),
    path("pet-types/delete/<int:pk>/", views.pet_type_delete, name="pet_type_delete"),

    # Breed URLs
    path("breeds/", views.breed_list, name="breed_list"),
    path("breeds/add/", views.breed_create, name="breed_create"),
    path("breeds/edit/<int:pk>/", views.breed_update, name="breed_update"),
    path("breeds/delete/<int:pk>/", views.breed_delete, name="breed_delete"),

]
