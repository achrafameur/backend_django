from django.contrib import admin
from django.urls import path, include

from professionnel.views import AddMenuAPIView, UpdateMenuAPIView, DeleteMenuAPIView, \
    GetAllMenusAPIView, MenuDetailAPIView, RestaurantOrdersAPIView, RestaurantStatsAPIView, \
    VerifyProfessionalAPIView, DeclineProfessionalAPIView, GetListOfProfToVerify, \
    GetRestaurantByIdAPIView, ActivateProfessionalAPIView, DesactivateProfessionalAPIView, \
    GetAvailableSeatsAPIView, UpdateAvailableSeatsAPIView

urlpatterns = [
    path('menu/add/', AddMenuAPIView.as_view(), name='add-menu'),
    path('menu/update/<int:menu_id>/', UpdateMenuAPIView.as_view(), name='update-menu'),
    path('menu/delete/<int:menu_id>/', DeleteMenuAPIView.as_view(), name='delete-menu'),
    path('menus/', GetAllMenusAPIView.as_view(), name='get-all-menus'),
    path('menu/<int:menu_id>/', MenuDetailAPIView.as_view(), name='menu_detail'),
    path('restaurant/<int:restaurant_id>/', GetRestaurantByIdAPIView.as_view(), name='get-restaurant-by-id'),
    path('commandes/<int:restaurant_id>/', RestaurantOrdersAPIView.as_view(), name='commands-list'),
    path('stats/<int:restaurant_id>/', RestaurantStatsAPIView.as_view(), name='stats'),
    path('verifier-professionnel/<int:admin_id>/', VerifyProfessionalAPIView.as_view(), name='verifier_professionnel'),
    path('refuser-professionnel/<int:admin_id>/', DeclineProfessionalAPIView.as_view(), name='refuser_professionnel'),
    path('desactivate-professionnel/<int:admin_id>/', DesactivateProfessionalAPIView.as_view(), name='verifier_professionnel'),
    path('activate-professionnel/<int:admin_id>/', ActivateProfessionalAPIView.as_view(), name='refuser_professionnel'),
    path('admins/list-professionnels/', GetListOfProfToVerify.as_view(), name='get-list-professionnels'),
    path('seats/', GetAvailableSeatsAPIView.as_view(), name='get-all-seats'),
    path('seats/update/<int:restaurant_id>/', UpdateAvailableSeatsAPIView.as_view(), name='update-seats'),
]
