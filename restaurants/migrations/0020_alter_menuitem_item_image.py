# Generated by Django 5.1.1 on 2024-12-07 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0019_menuitem_item_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='item_image',
            field=models.BinaryField(blank=True, default=None, null=True),
        ),
    ]
