from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static   # <-- required

urlpatterns = [
    path('admin/', admin.site.urls),

    # Include MyLogin app URLs
    path('', include('MyLogin.urls')),
]

# Serve uploaded media files (profile pictures, resumes)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
