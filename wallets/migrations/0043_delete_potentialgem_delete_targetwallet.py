# Generated by Django 4.0.8 on 2023-12-18 22:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0042_remove_ownedtoken_balance_change_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PotentialGem',
        ),
        migrations.DeleteModel(
            name='TargetWallet',
        ),
    ]
