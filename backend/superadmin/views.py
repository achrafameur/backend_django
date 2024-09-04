from datetime import date, datetime, time
from datetime import timedelta
from unittest import result
from venv import logger
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from django.http import HttpResponse
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.authentication import SessionAuthentication, BasicAuthentication
# from django.core import serializers
from django.utils.html import escape
import html
from environ import Env
from backend.models import Admins, Menu
from backend.serializers import AdminSerializer, MenuSerializer
from django.contrib.auth.hashers import make_password, check_password
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from rest_framework.response import Response


env = Env()
env.read_env()
  
class UpdateAdminAPIView(APIView):
    def put(self, request, admin_id):
        try:
            admin = Admins.objects.get(id=admin_id)
        except Admins.DoesNotExist:
            return JsonResponse({"message": "Admin not found"}, status=status.HTTP_404_NOT_FOUND)

        # Si un fichier 'avatar' est présent dans la requête, mettez à jour l'avatar
        if 'avatar' in request.data:
            admin.avatar = request.data['avatar']
        
        serializer = AdminSerializer(admin, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"message": "Admin updated successfully"})
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DeleteAdminAPIView(APIView):
    def delete(self, request, admin_id):
        try:
            admin = Admins.objects.get(id=admin_id)
            admin.delete()
            return JsonResponse({"message": "Admin deleted successfully"})
        except Admins.DoesNotExist:
            return JsonResponse({"message": "Admin not found"}, status=status.HTTP_404_NOT_FOUND)
        
class GetSuperAdminsAPIView(APIView):
    def get(self, request):
        super_admins = Admins.objects.filter(id_service=0)
        serializer = AdminSerializer(super_admins, many=True)
        return JsonResponse(serializer.data, safe=False)
    
class GetClientsAPIView(APIView):
    def get(self, request):
        clients = Admins.objects.filter(id_service=1)
        serializer = AdminSerializer(clients, many=True)
        return JsonResponse(serializer.data, safe=False)
    
class GetProfessionnelsAPIView(APIView):
    def get(self, request):
        professionnels = Admins.objects.filter(id_service=2)
        professionnel_data = []

        for professionnel in professionnels:
            # Serialize the professional's data
            serializer = AdminSerializer(professionnel)
            data = serializer.data
            
            # Get the related menus
            menus = Menu.objects.filter(admin=professionnel)
            menu_serializer = MenuSerializer(menus, many=True)
            
            # Add the menus to the professional's data
            data['menus'] = menu_serializer.data
            professionnel_data.append(data)

        return JsonResponse(professionnel_data, safe=False, status=status.HTTP_200_OK)


class GetMenusByAdminAPIView(APIView):
    def get(self, request, admin_id):
        try:
            admin = Admins.objects.get(id=admin_id)
            menus = Menu.objects.filter(admin=admin)
            serializer = MenuSerializer(menus, many=True)
            return JsonResponse(serializer.data, safe=False)
        except Admins.DoesNotExist:
            return JsonResponse({"message": "Admin not found"}, status=status.HTTP_404_NOT_FOUND)
      
class ProfessionnelSearchAPIView(APIView):
    def get(self, request):
        query = request.GET.get('query', '').lower()
        if query:
            professionnels = Admins.objects.filter(
                Q(adresse_mail__icontains=query) |
                Q(nom_organisme__icontains=query),
                id_service = 2
            )
            serializer = AdminSerializer(professionnels, many=True)
            return JsonResponse(serializer.data,safe=False , status=status.HTTP_200_OK)
        return JsonResponse({"message": "No query provided"}, status=status.HTTP_400_BAD_REQUEST)
    
class ClientsSearchAPIView(APIView):
    def get(self, request):
        query = request.GET.get('query', '').lower()
        if query:
            clients = Admins.objects.filter(
                Q(adresse_mail__icontains=query) |
                Q(nom__icontains=query) |
                Q(prenom__icontains=query),
                id_service = 1
            )
            serializer = AdminSerializer(clients, many=True)
            return JsonResponse(serializer.data,safe=False , status=status.HTTP_200_OK)
        return JsonResponse({"message": "No query provided"}, status=status.HTTP_400_BAD_REQUEST)
    
class AdminsSearchAPIView(APIView):
    def get(self, request):
        query = request.GET.get('query', '').lower()
        if query:
            admins = Admins.objects.filter(
                Q(adresse_mail__icontains=query) |
                Q(nom__icontains=query) |
                Q(prenom__icontains=query),
                id_service = 0
            )
            serializer = AdminSerializer(admins, many=True)
            return JsonResponse(serializer.data,safe=False , status=status.HTTP_200_OK)
        return JsonResponse({"message": "No query provided"}, status=status.HTTP_400_BAD_REQUEST)
    
class PendingMenusListAPIView(APIView):
    def get(self, request):
        pending_menus = Menu.objects.filter(is_approuved=False, is_declined=False)
        serializer = MenuSerializer(pending_menus, many=True)
        return JsonResponse(serializer.data, safe=False)


class ApproveDeclineMenuAPIView(APIView):
    def post(self, request):
        menu_id = request.data.get('menu_id')
        action = request.data.get('action')
        admin_id = request.data.get('admin_id')

        if not menu_id or not action or not admin_id:
            return JsonResponse({'error': 'Menu ID, action, and admin ID are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            menu = Menu.objects.get(id=menu_id)
        except Menu.DoesNotExist:
            return JsonResponse({'error': 'Menu not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            admin = Admins.objects.get(id=admin_id)
        except Admins.DoesNotExist:
            return JsonResponse({'error': 'Admin not found'}, status=status.HTTP_404_NOT_FOUND)

        if action == 'approve':
            menu.is_approuved = True
            menu.is_declined = False
        elif action == 'decline':
            menu.is_approuved = False
            menu.is_declined = True
        else:
            return JsonResponse({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        menu.approved_by = admin
        menu.save()

        return JsonResponse({'message': f'Menu has been {action}d by Admin ID {admin_id}'}, status=status.HTTP_200_OK)


class VerifyProfessionalAPIView(APIView):
    def get(self, request, admin_id):
        try:
            admin = Admins.objects.get(id=admin_id, id_service=2)
        except Admins.DoesNotExist:
            return JsonResponse({'error': 'Admin not found'}, status=status.HTTP_404_NOT_FOUND)

        if admin.is_verified:
            logger.debug("Le professionnel est déjà vérifié.")
            return JsonResponse({'status': 'already_verified', 'message': 'Le professionnel est déjà vérifié.'})

        admin.is_verified = True
        admin.save()
        logger.debug("Le professionnel a été vérifié avec succès.")
        
        return JsonResponse({'status': 'success', 'message': 'Le professionnel a été vérifié avec succès.'}, status=status.HTTP_200_OK)
    


class DeclineProfessionalAPIView(APIView):
    def get(self, request, admin_id):

        if not admin_id:
            return JsonResponse({'error': 'Admin ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            admin = Admins.objects.get(id=admin_id, id_service=2, is_verified=0)
        except Admins.DoesNotExist:
            return JsonResponse({'error': 'Admin not found'}, status=status.HTTP_404_NOT_FOUND)

        if admin.is_declined:
            logger.debug("Le professionnel est déjà refusé.")
            return JsonResponse({'status': 'already_declined', 'message': 'Le professionnel est déjà refusé.'})

        admin.is_declined = True
        admin.save()
        logger.debug("Le professionnel a été refusé avec succès.")
        
        return JsonResponse({'status': 'success', 'message': 'Le professionnel a été refusé avec succès.'}, status=status.HTTP_200_OK)



class GetListOfProfToVerify(APIView):
    def get(self, request):
        professionnels = Admins.objects.filter(id_service=2, is_verified=False, is_declined=False)
        serializer = AdminSerializer(professionnels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)