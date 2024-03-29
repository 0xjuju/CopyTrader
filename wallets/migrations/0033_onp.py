# Generated by Django 4.0.8 on 2023-11-20 02:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0032_walletfilter_min_token_wins'),
    ]

    operations = [
        migrations.CreateModel(
            name='ONP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255)),
                ('symbol', models.CharField(default='', max_length=255)),
                ('token_id', models.CharField(default='', max_length=255)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('price_change', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
            ],
        ),
    ]
