from datetime import date, datetime, time
from datetime import timedelta
from unittest import result
from django.shortcuts import get_object_or_404, redirect
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
import logging
from django.contrib.auth.decorators import user_passes_test
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


logger = logging.getLogger(__name__)

def verifier_professionnel(request, admin_id):
    logger.debug(f"Tentative de vérification du professionnel avec l'ID : {admin_id}")
    admin = get_object_or_404(Admins, id=admin_id, id_service=2)
    
    if admin.is_verified:
        logger.debug("Le professionnel est déjà vérifié.")
        return JsonResponse({'status': 'already_verified', 'message': 'Le professionnel est déjà vérifié.'})
    
    admin.is_verified = True
    admin.save()
    logger.debug("Le professionnel a été vérifié avec succès.")
    
    return JsonResponse({'status': 'success', 'message': 'Le professionnel a été vérifié avec succès.'})
