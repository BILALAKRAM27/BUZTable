# Generated by Django 5.1.1 on 2024-12-09 22:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0021_special_deals_deal_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='indoor_tables',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='outdoor_tables',
        ),
    ]
