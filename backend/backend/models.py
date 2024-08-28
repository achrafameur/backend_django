from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser
from django.utils import timezone
from backend.managers import CustomUserManager
from cloudinary.models import CloudinaryField
from django.core.exceptions import ValidationError

class Admins(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=255, null=True, blank=True)
    prenom = models.CharField(max_length=255, null=True, blank=True)
    nom_organisme = models.CharField(max_length=255, null=True, blank=True)
    num_siret = models.CharField(max_length=14, null=True, blank=True)
    adresse_mail = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    id_service = models.IntegerField(choices=[(0, 'super_admin'), (1, 'client'), (2, 'professionnel')])
    is_verification_mail_set = models.BooleanField(default=False)
    avatar = CloudinaryField('avatar', blank=True, null=True)
    localisation = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "admins"

    def clean(self):
        if self.id_service == 2 and not self.localisation:
            raise ValidationError('Localisation is required for service "professionnel".')
        

class Menu(models.Model):
    admin = models.ForeignKey(Admins, on_delete=models.CASCADE, related_name='menus')
    nom_organisme = models.CharField(max_length=255, null=True, blank=True)
    nom = models.CharField(max_length=100)
    description = models.TextField()
    image = CloudinaryField('image', blank=True, null=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    number_dispo = models.PositiveIntegerField(default=0)
    is_approuved = models.BooleanField(default=False)

    class Meta:
        db_table = "menus"

    def save(self, *args, **kwargs):
        if self.admin:
            self.nom_organisme = self.admin.nom_organisme
        super().save(*args, **kwargs)
        

class FavorisRestaurant(models.Model):
    user = models.ForeignKey(Admins, on_delete=models.CASCADE, related_name='favoris_restaurants')
    restaurant = models.ForeignKey(Admins, on_delete=models.CASCADE, related_name='favoris_par_users')
    class Meta:
        db_table = "favoris_restaurant"
        unique_together = ('user', 'restaurant')
    def clean(self):
        if self.user.id_service != 1 or self.restaurant.id_service != 2:
            raise ValidationError('User must be a client (id_service=1) and restaurant must be a professionnel (id_service=2)')

class FavorisMenu(models.Model):
    user = models.ForeignKey(Admins, on_delete=models.CASCADE, related_name='favoris_menus')
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='favoris_par_users')
    class Meta:
        db_table = "favoris_menu"
        unique_together = ('user', 'menu')
    def clean(self):
        if self.user.id_service != 1:
            raise ValidationError('User must be a client (id_service=1)')
        
class Panier(models.Model):
    utilisateur = models.ForeignKey(Admins, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "panier"

class PanierItem(models.Model):
    panier = models.ForeignKey(Panier, related_name='items', on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    
    class Meta:
        db_table = "panier_item"

    def total(self):
        return self.menu.prix * self.quantite

class Commande(models.Model):
    utilisateur = models.ForeignKey(Admins, on_delete=models.CASCADE)
    panier = models.OneToOneField(Panier, on_delete=models.CASCADE)
    reference = models.CharField(max_length=255, unique=True)
    date_commande = models.DateTimeField(auto_now_add=True)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    est_payee = models.BooleanField(default=False)

    class Meta:
        db_table = "commande"

class RestaurantSeats(models.Model):
    restaurant = models.ForeignKey(Admins, on_delete=models.CASCADE)
    available_seats = models.IntegerField(default=0)

    class Meta:
        db_table = "restaurant_seats"

class Token(models.Model):
    token = models.fields.TextField()
    user_id = models.fields.IntegerField()
    created_at = models.fields.DateTimeField(default=timezone.now, blank=True, null=True, max_length=0)
    class Meta:
        db_table = "token"

class Admins_token(models.Model):
    token = models.fields.TextField()
    admin = models.ForeignKey(Admins, on_delete=models.CASCADE)
    created_at = models.fields.DateTimeField(default=timezone.now, blank=True, null=True, max_length=0)
    class Meta:
        db_table = "admins_token"


