# Generated by Django 4.0.8 on 2023-11-23 22:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coingecko', '0006_address_geckotoken_address'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='geckotoken',
            name='address',
        ),
        migrations.AddField(
            model_name='address',
            name='chain',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='address',
            name='token',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='coingecko.geckotoken'),
        ),
    ]
