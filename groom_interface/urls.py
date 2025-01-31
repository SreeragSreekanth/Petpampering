from django.urls import path
from . import views

urlpatterns = [
    path('groomdashboard/', views.groomer_dashboard, name='groomer_dashboard'),
    path("add-service/", views.add_service, name="add_service"),
    path('editprofile/', views.edit_profile, name='edit_profile'),
    path('services/', views.manage_services, name='manage_services'),
    path('services/edit/<int:service_id>/', views.edit_service, name='edit_service'),
    path('services/delete/<int:service_id>/', views.delete_service, name='delete_service'),
    path('services/view/<int:service_id>/', views.view_service, name='view_service'),
    path('appointments/', views.manage_appointments, name='manage_appointments'),
    path('appointments/update/<int:appointment_id>/<str:status>/', views.update_appointment_status, name='update_appointment'),

]
