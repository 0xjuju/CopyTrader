# Generated by Django 4.0.8 on 2023-12-29 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blockchain', '0003_factorycontract'),
    ]

    operations = [
        migrations.AddField(
            model_name='factorycontract',
            name='address',
            field=models.CharField(default='', max_length=255),
        ),
    ]