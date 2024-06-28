from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser
from django.utils import timezone
from pfe.managers import CustomUserManager
from cloudinary.models import CloudinaryField


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

    class Meta:
        db_table = "admins"
class Menu(models.Model):
    admin = models.ForeignKey(Admins, on_delete=models.CASCADE, related_name='menus')
    nom = models.CharField(max_length=100)
    description = models.TextField()
    image = CloudinaryField('image', blank=True, null=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    number_dispo = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "menus"

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


