# Generated by Django 5.1.1 on 2024-11-25 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0003_remove_profile_dietary_preferences'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='restaurant_name',
            field=models.TextField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]
