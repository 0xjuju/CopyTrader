# Generated by Django 4.0.8 on 2024-01-16 07:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0046_gem'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gem',
            old_name='address',
            new_name='contract_address',
        ),
    ]
