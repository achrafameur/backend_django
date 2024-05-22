from pfe.models import Clients, Admins
from rest_framework.serializers import ModelSerializer, CharField, SerializerMethodField, IntegerField


class ClientsSerializer(ModelSerializer):
    class Meta:
        model = Clients
        fields = '__all__'

class AdminSerializer(ModelSerializer):
    class Meta:
        model = Admins
        fields = ['id', 'nom', 'prenom', 'nom_organisme', 'num_siret', 'adresse_mail', 'password', 'id_service', 'is_verification_mail_set']