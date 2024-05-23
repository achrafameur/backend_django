from pfe.models import Admins
from rest_framework.serializers import ModelSerializer, CharField, SerializerMethodField, IntegerField


class AdminSerializer(ModelSerializer):
    class Meta:
        model = Admins
        fields = ['id', 'nom', 'prenom', 'nom_organisme', 'num_siret', 'adresse_mail', 'password', 'id_service', 'is_verification_mail_set']