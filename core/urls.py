from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # 1. The Admin site MUST be first
    path('admin/', admin.site.urls),
    
    # 2. Your class app routes
    path('', include('classes.urls')),
    
    # 3. Built-in auth (Login/Logout)
    path('accounts/', include('django.contrib.auth.urls')),
]