# Generated by Django 5.1.3 on 2024-12-12 15:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0030_order_address_order_full_name_order_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='special_deal',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='restaurants.special_deals'),
        ),
    ]
