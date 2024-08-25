from django.contrib import admin
from django.urls import path, include
from .views import AddFavorisRestaurantAPIView, DeleteFavorisRestaurantAPIView, GetAllFavorisRestaurantsAPIView, \
    AddFavorisMenuAPIView, DeleteFavorisMenuAPIView, GetAllFavorisMenusAPIView, AddToPanierAPIView, UpdatePanierItemAPIView, \
    DeletePanierItemAPIView, ValidatePanierAPIView, GetPanierAPIView

urlpatterns = [
    # Verified
    path('favoris/restaurants/', AddFavorisRestaurantAPIView.as_view(), name='add_favoris_restaurant'),
    path('favoris/restaurants/<int:restaurant_id>/', DeleteFavorisRestaurantAPIView.as_view(), name='delete_favoris_restaurant'),
    path('favoris/restaurants/list/', GetAllFavorisRestaurantsAPIView.as_view(), name='list_favoris_restaurants'),

    # Verified
    path('favoris/menus/', AddFavorisMenuAPIView.as_view(), name='add_favoris_menu'),
    path('favoris/menus/<int:menu_id>/', DeleteFavorisMenuAPIView.as_view(), name='delete_favoris_menu'),
    path('favoris/menus/list/', GetAllFavorisMenusAPIView.as_view(), name='list_favoris_menus'),

    # Verified
    path('panier/add/', AddToPanierAPIView.as_view(), name='add-to-panier'),
    path('panier/update/<int:item_id>/', UpdatePanierItemAPIView.as_view(), name='update-panier-item'),
    path('panier/delete/<int:item_id>/', DeletePanierItemAPIView.as_view(), name='delete-panier-item'),
    path('panier/validate/', ValidatePanierAPIView.as_view(), name='validate-panier'),
    path('panier/', GetPanierAPIView.as_view(), name='get-panier'),
]
