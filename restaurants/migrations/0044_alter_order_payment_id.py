# Generated by Django 5.1.1 on 2024-12-16 16:35

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0043_remove_order_menu_items_remove_order_quantities_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_id',
            field=models.CharField(blank=True, default=uuid.uuid4, max_length=255),
        ),
    ]
