# Generated by Django 5.1.1 on 2024-12-07 12:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0013_profile_wifi_reservation_wifi'),
    ]

    operations = [
        migrations.CreateModel(
            name='special_deals',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('items', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('order_count', models.PositiveIntegerField(default=0)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='special_deal', to='restaurants.profile')),
            ],
            options={
                'verbose_name': 'Special Deal',
                'verbose_name_plural': 'Special Deals',
            },
        ),
    ]
