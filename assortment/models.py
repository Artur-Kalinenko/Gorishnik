from django.db import models
from producer.models import Producer

# Основная модель товара
class Assortment(models.Model):
    assortment_name = models.CharField(max_length=200, verbose_name='Назва продукту')
    assortment_categories = models.ForeignKey('Category', on_delete=models.PROTECT, null=True, verbose_name='Назва категорії')
    price = models.FloatField(null=True, blank=True, verbose_name='Ціна продукту')
    grams = models.IntegerField(null=True, blank=True, verbose_name='Грамовка продукту')
    poster = models.ImageField(upload_to='assortment/posters/', null=True, blank=True, verbose_name='Картинка продукту')
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE, verbose_name='Назва виробника')
    assortment_description = models.TextField(null=True, verbose_name='Опис продукту')
    is_available = models.BooleanField(default=True, verbose_name='Наявність продукту')
    has_variants = models.BooleanField(default=False, verbose_name='Чи є варіанти продукту')

    def __str__(self):
        return f'{self.assortment_name}'

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'
        ordering = ['assortment_name']


# Вариант одного и того же товара (разные граммовки)
class AssortmentVariant(models.Model):
    assortment = models.ForeignKey(Assortment, on_delete=models.CASCADE, related_name='variants', verbose_name='Продукт')
    grams = models.IntegerField(verbose_name='Грамовка продукту')
    price = models.FloatField(verbose_name='Ціна за грамовку')

    def __str__(self):
        return f'{self.grams}г - ₴{self.price}'

    class Meta:
        verbose_name = 'Варіант продукту'
        verbose_name_plural = 'Варіанти продуктів'
        ordering = ['grams']


# Категория товара (например, горіхи, сухофрукти и т.д.)
class Category(models.Model):
    category = models.CharField(max_length=255, db_index=True, verbose_name='Категорія')
    button_icon = models.ImageField(upload_to='assortment/category_icons_buttons/', null=True, blank=True)
    display_icon = models.ImageField(upload_to='assortment/category_icons', blank=True, null=True)

    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'
        ordering = ['category']

    def __str__(self):
        return self.category
