# Generated by Django 4.0.8 on 2023-12-13 23:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coingecko', '0010_geckotoken_date_added_geckotoken_price_change_24hr_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ONP',
        ),
    ]
