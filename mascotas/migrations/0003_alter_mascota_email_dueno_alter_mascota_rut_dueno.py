# Generated by Django 5.2.4 on 2025-07-12 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mascotas', '0002_mascota_email_dueno_mascota_rut_dueno'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mascota',
            name='email_dueno',
            field=models.EmailField(max_length=254, verbose_name='Correo del dueño'),
        ),
        migrations.AlterField(
            model_name='mascota',
            name='rut_dueno',
            field=models.CharField(max_length=15, verbose_name='RUT del dueño'),
        ),
    ]
