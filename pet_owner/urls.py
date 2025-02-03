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
    path('services/', views.browse_services, name='browse_services'),
    path('book-appointment/<int:service_id>/', views.book_appointment, name='book_appointment'),
    path('appointments/', views.view_appointments, name='view_appointments'),
    path('reschedule-appointment/<int:appointment_id>/', views.reschedule_appointment, name='reschedule_appointment'),
    path('cancel-appointment/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('community/', views.community_posts, name='community_posts'),
    path('community/create/', views.create_community_post, name='create_community_post'),
    path('community/<int:post_id>/', views.view_community_post, name='view_post'),
    path('myservice/<int:service_id>/feedback/', views.leave_feedback, name='leave_feedback'),
    path('feedback/edit/<int:feedback_id>/', views.edit_feedback, name='edit_feedback'),
    path('feedback/delete/<int:feedback_id>/', views.delete_feedback, name='delete_feedback'),
]