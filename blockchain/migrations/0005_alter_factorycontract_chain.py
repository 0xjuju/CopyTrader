# Generated by Django 4.0.8 on 2024-01-03 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blockchain', '0004_factorycontract_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='factorycontract',
            name='chain',
            field=models.CharField(default='', max_length=255),
        ),
    ]
