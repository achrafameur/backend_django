from django.contrib import admin
from django.urls import path, include

from superadmin.views import UpdateAdminAPIView, DeleteAdminAPIView, \
    GetSuperAdminsAPIView, GetClientsAPIView, GetProfessionnelsAPIView, \
    GetMenusByAdminAPIView, ProfessionnelSearchAPIView, ClientsSearchAPIView, \
    AdminsSearchAPIView, PendingMenusListAPIView, ApproveDeclineMenuAPIView

urlpatterns = [
    path('admin/update/<int:admin_id>/', UpdateAdminAPIView.as_view(), name='update-admin'),
    path('admin/delete/<int:admin_id>/', DeleteAdminAPIView.as_view(), name='delete-admin'),
    path('admins/super_admins/', GetSuperAdminsAPIView.as_view(), name='get-super-admins'),
    path('admins/clients/', GetClientsAPIView.as_view(), name='get-clients'),
    path('admins/professionnels/', GetProfessionnelsAPIView.as_view(), name='get-professionnels'),
    path('admin/<int:admin_id>/menus/', GetMenusByAdminAPIView.as_view(), name='get-menus-by-admin'),
    path('admins/search_professionnels/', ProfessionnelSearchAPIView.as_view(), name='search-professionnels'),
    path('admins/search_clients/', ClientsSearchAPIView.as_view(), name='search-professionnels'),
    path('admins/search_super_admins/', AdminsSearchAPIView.as_view(), name='search-professionnels'),
    path('pending-menus/', PendingMenusListAPIView.as_view(), name='pending-menus-list'),
    path('approve-decline-menu/', ApproveDeclineMenuAPIView.as_view(), name='approve-decline-menu'),
]
