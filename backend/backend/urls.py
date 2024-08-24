from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from backend.views import InscriptionAPIView, ConnexionAPIView, ProfileAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('superadmin/', include('superadmin.urls')),
    path('professionnel/', include('professionnel.urls')),
    path('client/', include('client.urls')),
    path('api/inscription/', InscriptionAPIView.as_view(), name='inscription'),
    path('api/connexion/', ConnexionAPIView.as_view(), name='connexion'),
    path('api/profile/', ProfileAPIView.as_view(), name='profile'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
