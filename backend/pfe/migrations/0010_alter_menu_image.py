# Generated by Django 4.0.6 on 2024-05-24 09:20

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pfe', '0009_alter_menu_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menu',
            name='image',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image'),
        ),
    ]
