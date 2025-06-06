# Generated by Django 5.2.1 on 2025-05-15 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Producer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('producer_name', models.CharField(max_length=100, verbose_name='Назва виробника')),
                ('producer_country', models.CharField(max_length=100, verbose_name='Країна виробника')),
                ('producer_img', models.ImageField(blank=True, null=True, upload_to='producer/posters/', verbose_name='Логотип Виробника')),
                ('producer_description', models.TextField(null=True, verbose_name='Опис виробника')),
            ],
            options={
                'verbose_name': 'Виробник',
                'verbose_name_plural': 'Виробники',
                'ordering': ['producer_name'],
            },
        ),
    ]
