# Generated by Django 5.1.5 on 2025-05-17 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0004_cart_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
