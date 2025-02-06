from django.urls import path
from . import views
from .views import TestView


urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home_view, name='home'),
    path('test/', TestView.as_view(), name='test_view'),
]
