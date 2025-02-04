# urls.py
from django.urls import path
from . import views

urlpatterns = [

    path('notifications/', views.notification_list, name='notifications'),
    path('notifications/read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('mark_all_as_read/', views.mark_all_as_read, name='mark_all_as_read'),

]