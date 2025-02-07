# urls.py
from django.urls import path
from . import views

urlpatterns = [

    path('notifications/', views.notification_list, name='notifications'),
    path('notifications/read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('mark_all_as_read/', views.mark_all_as_read, name='mark_all_as_read'),
    path('pet_owner/expenses/', views.pet_owner_expenses, name='pet_owner_expenses'),

    # Groomer Views
    path('groomer/payments/', views.groomer_payments, name='groomer_payments'),
    path('update_payment_status/<int:appointment_id>/', views.update_payment_status, name='update_payment_status'),
    path('invoice/<int:invoice_id>/pdf/', views.generate_invoice_pdf, name='generate_invoice_pdf'),
    path('invoice/<int:invoice_id>/view/', views.view_invoice_pdf, name='view_invoice_pdf'),

    
]