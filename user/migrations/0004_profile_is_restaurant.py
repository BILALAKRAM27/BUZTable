# Generated by Django 5.1.1 on 2024-12-10 22:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_alter_profile_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_restaurant',
            field=models.BooleanField(default=False),
        ),
    ]
