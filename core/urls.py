from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # This line tells Django: "Go look inside classes/urls.py for everything else"
    path('', include('classes.urls')), 
    
    path('accounts/', include('django.contrib.auth.urls')),
]