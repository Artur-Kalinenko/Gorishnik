from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import (
    Assortment, AssortmentVariant, Category,
    FilterGroup, FilterOption, Tag, AssortmentAdminForm
)
from producer.models import Producer


# 🔹 Кастомная валидация: минимум 2 варианта, если включен флаг "є варіанти"
class AssortmentVariantInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        if self.instance.has_variants:
            valid_forms = [
                form for form in self.forms
                if not form.cleaned_data.get('DELETE', False)
                   and form.cleaned_data.get('grams') is not None
            ]
            if len(valid_forms) < 2:
                raise ValidationError("Якщо товар має варіанти, потрібно додати щонайменше 2.")

            if self.instance.is_discounted:
                # Проверяем, что у всех валидных вариантов заполнен old_price
                for form in valid_forms:
                    if not form.cleaned_data.get('old_price'):
                        raise ValidationError("Усі варіанти акційного товару повинні мати заповнене поле old_price.")


# Варианты (граммовки) отображаются прямо внутри товара
class AssortmentVariantInline(admin.TabularInline):
    model = AssortmentVariant
    formset = AssortmentVariantInlineFormSet
    extra = 1
    fields = ['grams', 'price', 'old_price']
    min_num = 0
    max_num = 10


# Админка для модели Assortment (товар)
@admin.register(Assortment)
class AssortmentAdmin(admin.ModelAdmin):
    form = AssortmentAdminForm
    list_display = ['assortment_name', 'get_categories', 'producer', 'price', 'old_price', 'is_discounted', 'is_available']
    list_filter = ['producer', 'is_available', 'is_discounted']
    search_fields = ['assortment_name']
    inlines = [AssortmentVariantInline]
    filter_horizontal = ['filters', 'tags', 'assortment_categories']

    def get_categories(self, obj):
        return ", ".join([cat.category for cat in obj.assortment_categories.all()])
    get_categories.short_description = 'Категорії'


# Админка для категорий
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category']
    search_fields = ['category']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

# Админка для групп фильтров
@admin.register(FilterGroup)
class FilterGroupAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

# Админка для опций фильтров
@admin.register(FilterOption)
class FilterOptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'group']
    list_filter = ['group']
    search_fields = ['name']
