# Generated by Django 5.2.1 on 2025-06-14 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assortment', '0028_assortment_slug_category_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assortment',
            name='slug',
            field=models.SlugField(blank=True, max_length=100, unique=True, verbose_name='Slug'),
        ),
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(blank=True, max_length=100, unique=True, verbose_name='Slug'),
        ),
    ]
