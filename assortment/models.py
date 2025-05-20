from django.db import models
from django.core.exceptions import ValidationError
from producer.models import Producer
from django.conf import settings

# Основная модель товара
class Assortment(models.Model):
    assortment_name = models.CharField(max_length=200, verbose_name='Назва продукту')
    assortment_categories = models.ForeignKey('Category', on_delete=models.PROTECT, null=True, verbose_name='Назва категорії')
    filters = models.ManyToManyField('FilterOption', blank=True, related_name='products', verbose_name='Фільтри')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Ціна продукту')
    grams = models.IntegerField(null=True, blank=True, verbose_name='Грамовка продукту')
    poster = models.ImageField(upload_to='assortment/posters/', null=True, blank=True, verbose_name='Картинка продукту')
    producer = models.ForeignKey(Producer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Назва виробника')
    assortment_description = models.TextField(null=True, verbose_name='Опис продукту')
    is_available = models.BooleanField(default=True, verbose_name='Наявність продукту')
    has_variants = models.BooleanField(default=False, verbose_name='Чи є варіанти продукту')
    popularity = models.PositiveIntegerField(default=0, verbose_name='Популярність')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата додавання')

    def __str__(self):
        return f'{self.assortment_name}'

    def clean(self):
        if self.has_variants and (self.price or self.grams):
            raise ValidationError("Неможливо одночасно вказати фіксовану ціну/грамовку і вибрати 'є варіанти'.")

        if not self.has_variants and not self.price:
            raise ValidationError("Необхідно або вказати ціну, або активувати 'є варіанти'.")

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'
        ordering = ['assortment_name']


# Вариант одного и того же товара (разные граммовки)
class AssortmentVariant(models.Model):
    assortment = models.ForeignKey(Assortment, on_delete=models.CASCADE, related_name='variants', verbose_name='Продукт')
    grams = models.IntegerField(verbose_name='Грамовка продукту')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Ціна за грамовку')

    def __str__(self):
        return f'{self.grams}г - ₴{self.price}'

    class Meta:
        verbose_name = 'Варіант продукту'
        verbose_name_plural = 'Варіанти продуктів'
        ordering = ['grams']


# Категория товара
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


# Группа фильтров, например: "Орехи", "Восточные солодощі"
class FilterGroup(models.Model):
    name = models.CharField(max_length=255, verbose_name='Назва групи фільтрів')

    class Meta:
        verbose_name = 'Група фільтрів'
        verbose_name_plural = 'Групи фільтрів'
        ordering = ['name']

    def __str__(self):
        return self.name


# Конкретная опція фильтра, например: "Фундук", "Кешью"
class FilterOption(models.Model):
    group = models.ForeignKey(FilterGroup, on_delete=models.CASCADE, related_name='options', verbose_name='Група')
    name = models.CharField(max_length=255, verbose_name='Назва опції')

    class Meta:
        verbose_name = 'Опція фільтра'
        verbose_name_plural = 'Опції фільтрів'
        ordering = ['group', 'name']
        unique_together = ('group', 'name')

    def __str__(self):
        return f"{self.group.name} → {self.name}"
