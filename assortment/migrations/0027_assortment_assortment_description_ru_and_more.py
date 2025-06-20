# Generated by Django 5.2.1 on 2025-06-11 06:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assortment', '0026_category_cover_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='assortment',
            name='assortment_description_ru',
            field=models.TextField(help_text='Короткий опис або інструкція', null=True, verbose_name='Опис продукту'),
        ),
        migrations.AddField(
            model_name='assortment',
            name='assortment_description_uk',
            field=models.TextField(help_text='Короткий опис або інструкція', null=True, verbose_name='Опис продукту'),
        ),
        migrations.AddField(
            model_name='assortment',
            name='assortment_name_ru',
            field=models.CharField(help_text='Наприклад: Кешʼю смажений, Фініки королівські', max_length=200, null=True, verbose_name='Назва продукту'),
        ),
        migrations.AddField(
            model_name='assortment',
            name='assortment_name_uk',
            field=models.CharField(help_text='Наприклад: Кешʼю смажений, Фініки королівські', max_length=200, null=True, verbose_name='Назва продукту'),
        ),
        migrations.AddField(
            model_name='category',
            name='category_ru',
            field=models.CharField(db_index=True, max_length=255, null=True, verbose_name='Категорія'),
        ),
        migrations.AddField(
            model_name='category',
            name='category_uk',
            field=models.CharField(db_index=True, max_length=255, null=True, verbose_name='Категорія'),
        ),
        migrations.AddField(
            model_name='filtergroup',
            name='name_ru',
            field=models.CharField(max_length=255, null=True, verbose_name='Назва групи фільтрів'),
        ),
        migrations.AddField(
            model_name='filtergroup',
            name='name_uk',
            field=models.CharField(max_length=255, null=True, verbose_name='Назва групи фільтрів'),
        ),
        migrations.AddField(
            model_name='filteroption',
            name='name_ru',
            field=models.CharField(max_length=255, null=True, verbose_name='Назва опції'),
        ),
        migrations.AddField(
            model_name='filteroption',
            name='name_uk',
            field=models.CharField(max_length=255, null=True, verbose_name='Назва опції'),
        ),
        migrations.AddField(
            model_name='tag',
            name='name_ru',
            field=models.CharField(max_length=50, null=True, unique=True, verbose_name='Назва мітки'),
        ),
        migrations.AddField(
            model_name='tag',
            name='name_uk',
            field=models.CharField(max_length=50, null=True, unique=True, verbose_name='Назва мітки'),
        ),
    ]
