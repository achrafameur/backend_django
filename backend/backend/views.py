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
from pfe.models import Clients, Admins
from backend.serializers import ClientsSerializer, AdminSerializer
from django.contrib.auth.hashers import make_password, check_password


env = Env()
env.read_env()

def salutView(request):
    return HttpResponse('Salut les gens')

class GetAllClientsAPIView(APIView):
    def post(self, request):
        try :
            clients = Clients.objects.all()
            serializer = ClientsSerializer(clients, many=True)
            return JsonResponse({ 'clients': serializer.data }, safe=False)
        except:
            return JsonResponse({"msg": "Error while getting the courses"}, status=status.HTTP_400_BAD_REQUEST)
        
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
                admin_id = admin.id
                id_service = admin.id_service
                message = f"Connexion réussie. Connecté en tant que "
                if id_service == 0:
                    message += "super admin"
                elif id_service == 1:
                    message += "client"
                elif id_service == 2:
                    message += "professionnel"
                return JsonResponse({"message": message, "admin_id": admin_id})
            else:
                return JsonResponse({"message": "Mot de passe incorrect"}, status=status.HTTP_400_BAD_REQUEST)
        except Admins.DoesNotExist:
            return JsonResponse({"message": "Aucun utilisateur trouvé avec cet e-mail"}, status=status.HTTP_400_BAD_REQUEST)
