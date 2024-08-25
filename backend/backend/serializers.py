from backend.models import Admins, Menu, FavorisRestaurant, FavorisMenu, PanierItem, Panier, Commande
from rest_framework.serializers import ModelSerializer


class AdminSerializer(ModelSerializer):
    class Meta:
        model = Admins
        fields = ['id', 'nom', 'prenom', 'nom_organisme', 'num_siret', 'adresse_mail', 'password',
                'id_service', 'is_verification_mail_set', 'avatar', 'localisation']
    
class MenuSerializer(ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'
        extra_kwargs = {
            'image': {'required': False}
        }

class FavorisRestaurantSerializer(ModelSerializer):
    class Meta:
        model = FavorisRestaurant
        fields = ['id', 'restaurant']

class FavorisMenuSerializer(ModelSerializer):
    class Meta:
        model = FavorisMenu
        fields = ['id', 'menu']

class PanierItemSerializer(ModelSerializer):
    menu = MenuSerializer()

    class Meta:
        model = PanierItem
        fields = ['id', 'menu', 'quantite', 'total']

class PanierSerializer(ModelSerializer):
    items = PanierItemSerializer(many=True, read_only=True)

    class Meta:
        model = Panier
        fields = ['id', 'utilisateur', 'date_creation', 'items']

class CommandeSerializer(ModelSerializer):
    panier = PanierSerializer()
    
    class Meta:
        model = Commande
        fields = ['id', 'utilisateur', 'panier', 'reference', 'date_commande', 'montant_total', 'est_payee']