# Generated by Django 4.0.8 on 2023-12-18 01:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coingecko', '0011_delete_onp'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='decimals',
            field=models.IntegerField(default=18),
        ),
    ]