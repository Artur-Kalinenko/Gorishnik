# Generated by Django 5.2.1 on 2025-05-20 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assortment', '0010_tag_assortment_tags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assortment',
            name='assortment_categories',
        ),
        migrations.AddField(
            model_name='assortment',
            name='assortment_categories',
            field=models.ManyToManyField(related_name='assortments', to='assortment.category', verbose_name='Назва категорії'),
        ),
    ]
