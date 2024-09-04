from django.contrib import admin
from django.urls import path, include

from professionnel.views import AddMenuAPIView, UpdateMenuAPIView, DeleteMenuAPIView, \
    GetAllMenusAPIView, MenuDetailAPIView, RestaurantOrdersAPIView, RestaurantStatsAPIView

urlpatterns = [
    path('menu/add/', AddMenuAPIView.as_view(), name='add-menu'),
    path('menu/update/<int:menu_id>/', UpdateMenuAPIView.as_view(), name='update-menu'),
    path('menu/delete/<int:menu_id>/', DeleteMenuAPIView.as_view(), name='delete-menu'),
    path('menus/', GetAllMenusAPIView.as_view(), name='get-all-menus'),
    path('menu/<int:menu_id>/', MenuDetailAPIView.as_view(), name='menu_detail'),
    path('commandes/<int:restaurant_id>/', RestaurantOrdersAPIView.as_view(), name='commands-list'),
    path('stats/<int:restaurant_id>/', RestaurantStatsAPIView.as_view(), name='stats'),
]
