# Generated by Django 4.0.8 on 2023-12-14 03:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ABI',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('abi_type', models.CharField(default='', max_length=255)),
                ('text', models.TextField()),
            ],
        ),
    ]
