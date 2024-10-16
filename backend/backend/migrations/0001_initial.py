import cloudinary.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Admins',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nom', models.CharField(blank=True, max_length=255, null=True)),
                ('prenom', models.CharField(blank=True, max_length=255, null=True)),
                ('nom_organisme', models.CharField(blank=True, max_length=255, null=True)),
                ('num_siret', models.CharField(blank=True, max_length=14, null=True)),
                ('adresse_mail', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('id_service', models.IntegerField(choices=[(0, 'super_admin'), (1, 'client'), (2, 'professionnel')])),
                ('is_verification_mail_set', models.BooleanField(default=False)),
                ('avatar', cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='avatar')),
                ('localisation', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'admins',
            },
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom_organisme', models.CharField(blank=True, max_length=255, null=True)),
                ('nom', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('image', cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image')),
                ('prix', models.DecimalField(decimal_places=2, max_digits=10)),
                ('number_dispo', models.PositiveIntegerField(default=0)),
                ('is_approved', models.BooleanField(default=False)),
                ('is_declined', models.BooleanField(default=False)),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='menus', to='backend.admins')),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='approved_menus', to='backend.admins')),
            ],
            options={
                'db_table': 'menus',
            },
        ),
        migrations.CreateModel(
            name='Panier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('utilisateur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.admins')),
            ],
            options={
                'db_table': 'panier',
            },
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.TextField()),
                ('user_id', models.IntegerField()),
                ('created_at', models.DateTimeField(blank=True, default=django.utils.timezone.now, max_length=0, null=True)),
            ],
            options={
                'db_table': 'token',
            },
        ),
        migrations.CreateModel(
            name='RestaurantSeats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('available_seats', models.IntegerField(default=0)),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.admins')),
            ],
            options={
                'db_table': 'restaurant_seats',
            },
        ),
        migrations.CreateModel(
            name='PanierItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantite', models.PositiveIntegerField(default=1)),
                ('est_payee', models.BooleanField(default=False)),
                ('menu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.menu')),
                ('panier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='backend.panier')),
            ],
            options={
                'db_table': 'panier_item',
            },
        ),
        migrations.CreateModel(
            name='Commande',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.CharField(max_length=255, unique=True)),
                ('date_commande', models.DateTimeField(auto_now_add=True)),
                ('montant_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('est_payee', models.BooleanField(default=False)),
                ('panier', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='backend.panier')),
                ('utilisateur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.admins')),
            ],
            options={
                'db_table': 'commande',
            },
        ),
        migrations.CreateModel(
            name='Admins_token',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.TextField()),
                ('created_at', models.DateTimeField(blank=True, default=django.utils.timezone.now, max_length=0, null=True)),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.admins')),
            ],
            options={
                'db_table': 'admins_token',
            },
        ),
        migrations.CreateModel(
            name='FavorisRestaurant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favoris_par_users', to='backend.admins')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favoris_restaurants', to='backend.admins')),
            ],
            options={
                'db_table': 'favoris_restaurant',
                'unique_together': {('user', 'restaurant')},
            },
        ),
        migrations.CreateModel(
            name='FavorisMenu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('menu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favoris_par_users', to='backend.menu')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favoris_menus', to='backend.admins')),
            ],
            options={
                'db_table': 'favoris_menu',
                'unique_together': {('user', 'menu')},
            },
        ),
    ]
