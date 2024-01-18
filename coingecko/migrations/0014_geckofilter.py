# Generated by Django 4.0.8 on 2024-01-18 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coingecko', '0013_alter_geckotoken_price_change_24hr_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeckoFilter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255)),
                ('percentage_change_24h', models.IntegerField(default=0)),
                ('percentage_change_7d', models.IntegerField(default=0)),
                ('pages_to_parse', models.IntegerField(default=0)),
            ],
        ),
    ]
