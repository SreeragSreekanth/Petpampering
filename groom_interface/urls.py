from django.urls import path
from . import views

urlpatterns = [
    path('groomdashboard/', views.groomer_dashboard, name='groomer_dashboard'),
    path("add-service/", views.add_service, name="add_service"),
    path('editprofile/', views.edit_profile, name='edit_profile'),
    path('myservices/', views.manage_services, name='manage_services'),
    path('myservices/edit/<int:service_id>/', views.edit_service, name='edit_service'),
    path('myservices/delete/<int:service_id>/', views.delete_service, name='delete_service'),
    path('myservices/view/<int:service_id>/', views.view_service, name='view_service'),
    path('manageappointments/', views.manage_appointments, name='manage_appointments'),
    path('manageappointments/update/<int:appointment_id>/<str:status>/', views.update_appointment_status, name='update_appointment'),
    path('groomer/<int:groomer_id>/', views.groomer_profile, name='groomer_profile'),
    path('feedback/respond/<int:feedback_id>/', views.respond_to_feedback, name='respond_to_feedback'),
    path('respond_to_feedback/<int:feedback_id>/', views.respond_to_feedback, name='respond_to_feedback'),


]
