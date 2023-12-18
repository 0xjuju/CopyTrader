# Generated by Django 4.0.8 on 2023-12-18 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0041_ownedtoken_balance_change'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ownedtoken',
            name='balance_change',
        ),
        migrations.AddField(
            model_name='ownedtoken',
            name='balance_increase',
            field=models.BooleanField(default=False),
        ),
    ]