# Generated by Django 5.1.3 on 2024-12-14 22:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0037_delete_reservation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Table',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('max_guests', models.IntegerField()),
                ('available', models.BooleanField(default=True)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tables', to='restaurants.profile')),
            ],
        ),
    ]
