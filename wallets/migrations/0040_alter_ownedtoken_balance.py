# Generated by Django 4.0.8 on 2023-12-18 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0039_alter_ownedtoken_date_added'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ownedtoken',
            name='balance',
            field=models.BigIntegerField(default=0),
        ),
    ]
