from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from backend.views import InscriptionAPIView, ConnexionAPIView, ProfileAPIView, UpadateLocationAPIView, CheckLocationAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('superadmin/', include('superadmin.urls')),
    path('professionnel/', include('professionnel.urls')),
    path('client/', include('client.urls')),
    path('api/inscription/', InscriptionAPIView.as_view(), name='inscription'),
    path('api/connexion/', ConnexionAPIView.as_view(), name='connexion'),
    path('api/profile/', ProfileAPIView.as_view(), name='profile'),
    path('api/update-location/', UpadateLocationAPIView.as_view(), name='update-location'),
    path('api/check-location/', CheckLocationAPIView.as_view(), name='check-location'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
