# Generated by Django 4.0.8 on 2022-10-24 00:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0003_bot'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bot',
            old_name='private_key',
            new_name='address',
        ),
        migrations.AlterField(
            model_name='bot',
            name='name',
            field=models.CharField(default='', max_length=255),
        ),
    ]
