from django.db import models

class Clients(models.Model):
    # CharField correspond à un varchar max 255
    firstname = models.fields.CharField(max_length=50)
    lastname = models.fields.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.fields.CharField(max_length=100, default=None, blank=True, null=True)
    is_mail_sent_credentials = models.fields.IntegerField(default=0)
    accepted_conditions= models.fields.IntegerField(default=0)
    username = None

    # pour renommer la table en BDD
    class Meta:
        db_table = "clients"
        indexes = [
            models.Index(fields=['password'], name='password_idx'),
        ]

class Admins(models.Model):
    # CharField correspond à un varchar max 255
    firstname = models.fields.CharField(max_length=50)
    lastname = models.fields.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.fields.CharField(max_length=100, default=None, blank=True, null=True)
    is_mail_sent_credentials = models.fields.IntegerField(default=0)
    accepted_conditions= models.fields.IntegerField(default=0)

    # pour renommer la table en BDD
    class Meta:
        db_table = "admins"
        indexes = [
            models.Index(fields=['password'], name='password_idx_admins'),
        ]

class Professionnels(models.Model):
    # CharField correspond à un varchar max 255
    name = models.fields.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.fields.CharField(max_length=100, default=None, blank=True, null=True)
    is_mail_sent_credentials = models.fields.IntegerField(default=0)
    accepted_conditions= models.fields.IntegerField(default=0)

    # pour renommer la table en BDD
    class Meta:
        db_table = "professionnels"
        indexes = [
            models.Index(fields=['password'], name='password_idx_pro'),
        ]
        

