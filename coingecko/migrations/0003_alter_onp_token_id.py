# Generated by Django 4.0.8 on 2023-11-20 03:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coingecko', '0002_onp_rank'),
    ]

    operations = [
        migrations.AlterField(
            model_name='onp',
            name='token_id',
            field=models.CharField(default='', max_length=255, unique=True),
        ),
    ]