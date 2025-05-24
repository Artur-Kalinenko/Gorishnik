from django.db import models
from django.core.exceptions import ValidationError
from producer.models import Producer
from django.conf import settings
from django.db.models import Avg
from django import forms
from .validators import validate_image
from django.urls import reverse
from django.contrib.admin.widgets import FilteredSelectMultiple

# Основная модель товара
class Assortment(models.Model):
    assortment_name = models.CharField(
        max_length=200,
        verbose_name='Назва продукту',
        help_text='Наприклад: Кешʼю смажений, Фініки королівські'
    )
    assortment_categories = models.ManyToManyField(
        'Category', related_name='assortments', verbose_name='Назва категорії',
        help_text='Оберіть одну або декілька категорій'
    )
    filters = models.ManyToManyField(
        'FilterOption', blank=True, related_name='products', verbose_name='Фільтри',
        help_text='Оберіть відповідні фільтри для цього товару'
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Ціна продукту',
        help_text='Залишити порожнім, якщо товар має варіанти'
    )
    old_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Стара ціна',
        help_text='Вкажіть стару ціну, якщо товар акційний'
    )
    grams = models.IntegerField(
        null=True, blank=True, verbose_name='Грамовка продукту',
        help_text='Вкажіть вагу у грамах, якщо товар без варіантів'
    )
    poster = models.ImageField(
        upload_to='assortment/posters/', null=False, blank=False, verbose_name='Картинка продукту',
        help_text='Головне зображення продукту', validators=[validate_image]
    )
    producer = models.ForeignKey(
        Producer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Назва виробника'
    )
    assortment_description = models.TextField(
        null=True, verbose_name='Опис продукту', help_text='Короткий опис або інструкція'
    )
    is_available = models.BooleanField(
        default=True, verbose_name='Наявність продукту',
        help_text='Чи є товар у наявності'
    )
    has_variants = models.BooleanField(
        default=False, verbose_name='Чи є варіанти продукту',
        help_text='Відмітьте, якщо у товару є різні грамовки'
    )
    is_discounted = models.BooleanField(
        default=False, verbose_name='Акційний товар'
    )
    popularity = models.PositiveIntegerField(
        default=0, verbose_name='Популярність'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата додавання')
    tags = models.ManyToManyField(
        'Tag', blank=True, related_name='products', verbose_name='Мітки',
        help_text='Можна обрати декілька міток'
    )

    def __str__(self):
        return f'{self.assortment_name}'

    def clean(self):
        super().clean()

        if self.has_variants and (self.price or self.grams):
            raise ValidationError("Неможливо одночасно вказати фіксовану ціну/грамовку і вибрати 'є варіанти'.")

        if not self.has_variants and not self.price:
            raise ValidationError("Необхідно або вказати ціну, або активувати 'є варіанти'.")

        if self.has_variants and self.old_price:
            raise ValidationError("У товару з варіантами не може бути вказана стара ціна безпосередньо в товарі.")

        if not self.has_variants:
            self.is_discounted = bool(self.old_price)

        if self.grams is not None and self.grams <= 0:
            raise ValidationError("Грамовка повинна бути більше 0.")

    @property
    def average_rating(self):
        return self.reviews.aggregate(avg=Avg('rating'))['avg'] or 0

    @property
    def is_new(self):
        from django.utils import timezone
        return self.created_at >= timezone.now() - timezone.timedelta(days=30)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'
        ordering = ['assortment_name']



# Вариант одного и того же товара (разные граммовки)
class AssortmentVariant(models.Model):
    assortment = models.ForeignKey(Assortment, on_delete=models.CASCADE, related_name='variants', verbose_name='Продукт')
    grams = models.IntegerField(verbose_name='Грамовка продукту')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Ціна за грамовку')
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Стара ціна')

    def __str__(self):
        return f'{self.grams}г - ₴{self.price}'

    class Meta:
        verbose_name = 'Варіант продукту'
        verbose_name_plural = 'Варіанти продуктів'
        ordering = ['grams']


# Модель тегов для товара
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Назва мітки')

    class Meta:
        verbose_name = 'Мітка'
        verbose_name_plural = 'Мітки'
        ordering = ['name']

    def __str__(self):
        return self.name



# Категория товара
class Category(models.Model):
    category = models.CharField(max_length=255, db_index=True, verbose_name='Категорія')
    button_icon_white = models.ImageField(upload_to='assortment/category_icons_buttons/', null=True, blank=True)
    button_icon_brown = models.ImageField(upload_to='assortment/category_icons', blank=True, null=True)

    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'
        ordering = ['category']

    def __str__(self):
        return self.category

    def get_absolute_url(self):
        return reverse('assortment_list') + f'?category={self.category}'

    def delete(self, *args, **kwargs):
        if self.assortments.exists():  # ← Используем related_name
            raise ValidationError("Неможливо видалити категорію, оскільки до неї прив'язані товари.")
        super().delete(*args, **kwargs)

# Отзывы о товаре
class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Користувач')
    assortment = models.ForeignKey(Assortment, on_delete=models.CASCADE, related_name='reviews', verbose_name='Продукт')
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)], verbose_name='Оцінка')
    comment = models.TextField(blank=True, verbose_name='Відгук')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'assortment')  # 1 отзыв от пользователя
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} → {self.assortment} ({self.rating})"

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

# не уверен надо ли
class AssortmentAdminForm(forms.ModelForm):
    class Meta:
        model = Assortment
        fields = '__all__'

    def clean_filters(self):
        filters = self.cleaned_data.get('filters')
        if not filters:
            raise forms.ValidationError("Товар повинен мати хоча б один фільтр.")
        return filters


class AssortmentImage(models.Model):
    assortment = models.ForeignKey(Assortment, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='assortment/gallery/', verbose_name='Фото в галереї', validators=[validate_image])

    def __str__(self):
        return f'Зображення для {self.assortment}'

    class Meta:
        verbose_name = 'Зображення товару'
        verbose_name_plural = 'Галерея зображень'
