# Generated by Django 4.1 on 2022-09-11 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0005_token_chain'),
    ]

    operations = [
        migrations.CreateModel(
            name='PoolContract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255)),
                ('address', models.CharField(default='', max_length=255)),
            ],
        ),
    ]