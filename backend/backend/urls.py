"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from backend.views import salutView
from django.conf import settings
from django.conf.urls.static import static
from backend.views import InscriptionAPIView, ConnexionAPIView, ProfileAPIView, UpdateAdminAPIView, DeleteAdminAPIView, GetSuperAdminsAPIView, GetClientsAPIView,\
    GetProfessionnelsAPIView, AddMenuAPIView, UpdateMenuAPIView, DeleteMenuAPIView, GetMenusByAdminAPIView, GetAllMenusAPIView, MenuDetailAPIView

urlpatterns = [
    path('salut/', salutView),
    # path('admin/', admin.site.urls),
    path('api/inscription/', InscriptionAPIView.as_view(), name='inscription'),
    path('api/connexion/', ConnexionAPIView.as_view(), name='connexion'),
    path('api/profile/', ProfileAPIView.as_view(), name='profile'),
    path('admin/update/<int:admin_id>/', UpdateAdminAPIView.as_view(), name='update-admin'),
    path('admin/delete/<int:admin_id>/', DeleteAdminAPIView.as_view(), name='delete-admin'),
    path('admins/super_admins/', GetSuperAdminsAPIView.as_view(), name='get-super-admins'),
    path('admins/clients/', GetClientsAPIView.as_view(), name='get-clients'),
    path('admins/professionnels/', GetProfessionnelsAPIView.as_view(), name='get-professionnels'),
    path('menu/add/', AddMenuAPIView.as_view(), name='add-menu'),
    path('menu/update/<int:menu_id>/', UpdateMenuAPIView.as_view(), name='update-menu'),
    path('menu/delete/<int:menu_id>/', DeleteMenuAPIView.as_view(), name='delete-menu'),
    path('admin/<int:admin_id>/menus/', GetMenusByAdminAPIView.as_view(), name='get-menus-by-admin'),
    path('menus/', GetAllMenusAPIView.as_view(), name='get-all-menus'),
    path('menu/<int:menu_id>/', MenuDetailAPIView.as_view(), name='menu_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
