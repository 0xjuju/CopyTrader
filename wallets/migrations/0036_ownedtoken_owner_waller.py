# Generated by Django 4.0.8 on 2023-12-17 23:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0035_ownedtoken'),
    ]

    operations = [
        migrations.AddField(
            model_name='ownedtoken',
            name='owner_waller',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='wallets.wallet'),
        ),
    ]