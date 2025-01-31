from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings



urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('userauth.urls')),
    path('',include('admin_panel.urls')),
    path('',include('groom_interface.urls')),
    path('',include('pet_owner.urls')),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)