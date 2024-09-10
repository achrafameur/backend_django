from backend.models import Admins, Menu, FavorisRestaurant, FavorisMenu, PanierItem, Panier, Commande, Litige, RestaurantSeats
from rest_framework.serializers import ModelSerializer


class AdminSerializer(ModelSerializer):
    class Meta:
        model = Admins
        fields = ['id', 'nom', 'prenom', 'nom_organisme', 'num_siret', 'adresse_mail',
                'id_service','avatar','password' ,'localisation','longitude','latitude', 'is_verified', 'is_declined']
    
class MenuSerializer(ModelSerializer):
    admin = AdminSerializer()
    class Meta:
        model = Menu
        fields = ['id', 'nom_organisme', 'nom', 'description', 'image', 'prix', 'number_dispo', 'is_approved', 'is_declined', 'type', 'admin']
        extra_kwargs = {
            'image': {'required': False}
        }

class MenuAddSerializer(ModelSerializer):
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

class RestaurantSeatsSerializer(ModelSerializer):
    
    class Meta:
        model = RestaurantSeats
        fields = ['id', 'available_seats', 'restaurant_id']

class LitigeSerializer(ModelSerializer):
    class Meta:
        model = Litige
        fields = ['id', 'titre', 'description', 'date_ajout', 'admin']