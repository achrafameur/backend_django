from backend.models import Admins, Menu
from rest_framework.serializers import ModelSerializer, CharField, SerializerMethodField, IntegerField


class AdminSerializer(ModelSerializer):
    class Meta:
        model = Admins
        fields = ['id', 'nom', 'prenom', 'nom_organisme', 'num_siret', 'adresse_mail', 'password', 'id_service', 'is_verification_mail_set', 'avatar']
    
class MenuSerializer(ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'
        extra_kwargs = {
            'image': {'required': False}
        }