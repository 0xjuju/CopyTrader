# Generated by Django 4.1 on 2022-09-05 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0002_rename_token_token_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='wallet',
            name='token',
            field=models.ManyToManyField(to='wallets.token'),
        ),
    ]
