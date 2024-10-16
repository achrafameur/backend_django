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
from environ import Env
from backend.models import Admins
from backend.serializers import AdminSerializer, MenuSerializer
from django.contrib.auth.hashers import make_password, check_password
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.shortcuts import get_object_or_404

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
        
class UpadateLocationAPIView(APIView):
    serializer_class = AdminSerializer

    def post(self, request, *args, **kwargs):
        admin_id = request.data.get('admin_id')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        try:
            admin = get_object_or_404(Admins, id=admin_id)
            admin.latitude = latitude
            admin.longitude = longitude
            admin.save()
            return JsonResponse({"message": "Location updated successfully"}, status=200)
        except Admins.DoesNotExist:
            return JsonResponse({'error': 'Admin not found'}, status=status.HTTP_404_NOT_FOUND)
        
class CheckLocationAPIView(APIView):
    def post(self, request):
        admin_id = request.data.get('admin_id')
        user = get_object_or_404(Admins, id=admin_id)

        if user.latitude is not None and user.longitude is not None:
            return JsonResponse({
                'location_enabled': True,
                'latitude': user.latitude,
                'longitude': user.longitude
            }, status=status.HTTP_200_OK)
        else:
            return JsonResponse({
                'location_enabled': False
            }, status=status.HTTP_200_OK)
