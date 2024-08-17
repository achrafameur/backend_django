from datetime import date, datetime, time
from datetime import timedelta
from unittest import result
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
from pfe.models import Admins, Menu
from backend.serializers import AdminSerializer, MenuSerializer
from django.contrib.auth.hashers import make_password, check_password
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q

env = Env()
env.read_env()

def salutView(request):
    return HttpResponse('Salut les gens')
        
class InscriptionAPIView(APIView):
    def post(self, request):
        serializer = AdminSerializer(data=request.data)
        if serializer.is_valid():
                # Hachage du mot de passe avant de le sauvegarder dans la base de données
                hashed_password = make_password(serializer.validated_data['password'])
                serializer.validated_data['password'] = hashed_password
                admin = serializer.save()
                return JsonResponse({"message": "Inscription réussie", "admin_id": admin.id})
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ConnexionAPIView(APIView):
    def post(self, request):
        email = request.data.get('adresse_mail')
        password = request.data.get('password')
        try:
            admin = Admins.objects.get(adresse_mail=email)
            if check_password(password, admin.password):
                # Création du JWT payload
                if admin.id_service == 0:
                    admin_type = 'super_admin'
                elif admin.id_service == 1:
                    admin_type = 'client'
                else:
                    admin_type = 'professionnel'
                # Création du JWT payload avec le type d'administrateur
                payload = {
                    'admin_id': admin.id,
                    'admin_type': admin_type,
                    'exp': datetime.utcnow() + timedelta(days=1)  # Token expire après 1 jour
                }
                # Génération du JWT token
                token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
                # Message de succès avec le token
                return JsonResponse({"message": "Connexion réussie", "token": token, "id_service": admin.id_service, "id": admin.id})
            else:
                return JsonResponse({"message": "Mot de passe incorrect"}, status=status.HTTP_400_BAD_REQUEST)
        except Admins.DoesNotExist:
            return JsonResponse({"message": "Aucun utilisateur trouvé avec cet e-mail"}, status=status.HTTP_400_BAD_REQUEST)
    
class ProfileAPIView(APIView):
    serializer_class = AdminSerializer

    def post(self, request, *args, **kwargs):
        admin_id = request.data.get('admin_id')
        try:
            admin = Admins.objects.get(id=admin_id)
            serializer = self.serializer_class(admin)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        except Admins.DoesNotExist:
            return JsonResponse({'error': 'Admin not found'}, status=status.HTTP_404_NOT_FOUND)
        
class UpdateAdminAPIView(APIView):
    # authentication_classes = [CustomAuthentication]
    parser_classes = [MultiPartParser, FormParser]

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
    # authentication_classes = [CustomAuthentication]

    def delete(self, request, admin_id):
        try:
            admin = Admins.objects.get(id=admin_id)
            admin.delete()
            return JsonResponse({"message": "Admin deleted successfully"})
        except Admins.DoesNotExist:
            return JsonResponse({"message": "Admin not found"}, status=status.HTTP_404_NOT_FOUND)
        
class GetSuperAdminsAPIView(APIView):
    # authentication_classes = [CustomAuthentication]

    def get(self, request):
        super_admins = Admins.objects.filter(id_service=0)
        serializer = AdminSerializer(super_admins, many=True)
        return JsonResponse(serializer.data, safe=False)
    
class GetClientsAPIView(APIView):
    # authentication_classes = [CustomAuthentication]

    def get(self, request):
        clients = Admins.objects.filter(id_service=1)
        serializer = AdminSerializer(clients, many=True)
        return JsonResponse(serializer.data, safe=False)
    
class GetProfessionnelsAPIView(APIView):
    # authentication_classes = [CustomAuthentication]

    def get(self, request):
        professionnels = Admins.objects.filter(id_service=2)
        serializer = AdminSerializer(professionnels, many=True)
        return JsonResponse(serializer.data, safe=False)
    

class AddMenuAPIView(APIView):
    # authentication_classes = [CustomAuthentication]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = MenuSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateMenuAPIView(APIView):
    # authentication_classes = [CustomAuthentication]

    def put(self, request, menu_id):
        try:
            menu = Menu.objects.get(id=menu_id)
        except Menu.DoesNotExist:
            return JsonResponse({"message": "Menu not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = MenuSerializer(menu, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteMenuAPIView(APIView):
    # authentication_classes = [CustomAuthentication]

    def delete(self, request, menu_id):
        try:
            menu = Menu.objects.get(id=menu_id)
            menu.delete()
            return JsonResponse({"message": "Menu deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Menu.DoesNotExist:
            return JsonResponse({"message": "Menu not found"}, status=status.HTTP_404_NOT_FOUND)

class GetMenusByAdminAPIView(APIView):
    # authentication_classes = [CustomAuthentication]

    def get(self, request, admin_id):
        try:
            admin = Admins.objects.get(id=admin_id)
            menus = Menu.objects.filter(admin=admin)
            serializer = MenuSerializer(menus, many=True)
            return JsonResponse(serializer.data, safe=False)
        except Admins.DoesNotExist:
            return JsonResponse({"message": "Admin not found"}, status=status.HTTP_404_NOT_FOUND)
        
class GetAllMenusAPIView(APIView):
    # authentication_classes = [CustomAuthentication]

    def get(self, request):
        menus = Menu.objects.all()
        serializer = MenuSerializer(menus, many=True)
        return JsonResponse(serializer.data, safe=False)
    

class MenuDetailAPIView(APIView):
    def get(self, request, menu_id):
        try:
            menu = Menu.objects.get(id=menu_id)
            serializer = MenuSerializer(menu)
            return JsonResponse(serializer.data, safe=False)
        except Menu.DoesNotExist:
            return JsonResponse({"message": "Menu not found"}, status=status.HTTP_404_NOT_FOUND)
        
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