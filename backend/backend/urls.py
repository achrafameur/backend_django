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
from backend.views import GetAllClientsAPIView, InscriptionAPIView, ConnexionAPIView, ProfileAPIView

urlpatterns = [
    path('salut/', salutView),
    # path('admin/', admin.site.urls),
    path('api/clients/getAll/', GetAllClientsAPIView.as_view()),
    path('api/inscription/', InscriptionAPIView.as_view(), name='inscription'),
    path('api/connexion/', ConnexionAPIView.as_view(), name='connexion'),
    path('api/profile/', ProfileAPIView.as_view(), name='profile'),
    # path('api/logout/', LogoutAPIView.as_view(), name='logout'),
]
