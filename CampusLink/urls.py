from django.contrib import admin
from django.urls import path, include  # include is important
from MyLogin import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Include MyLogin app URLs
    path('', include('MyLogin.urls')),  
]
