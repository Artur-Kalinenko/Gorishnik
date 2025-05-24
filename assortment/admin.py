from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from decimal import Decimal

from .models import (
    Assortment, AssortmentVariant, Category,
    FilterGroup, FilterOption, Tag, AssortmentAdminForm, AssortmentImage
)
from producer.models import Producer


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

            for form in valid_forms:
                price = form.cleaned_data.get('price')
                if price in [None, Decimal('0.00')]:
                    raise ValidationError("Кожен варіант повинен мати вказану ціну.")

            all_have_old_price = all(
                form.cleaned_data.get('old_price') not in [None, Decimal('0.00')]
                for form in valid_forms
            )

            none_have_old_price = all(
                form.cleaned_data.get('old_price') in [None, Decimal('0.00')]
                for form in valid_forms
            )

            if all_have_old_price:
                self.instance.is_discounted = True
            elif none_have_old_price:
                self.instance.is_discounted = False
            else:
                raise ValidationError("Усі варіанти акційного товару повинні мати заповнене поле old_price або жоден.")


class AssortmentVariantInline(admin.TabularInline):
    model = AssortmentVariant
    formset = AssortmentVariantInlineFormSet
    extra = 1
    fields = ['grams', 'price', 'old_price']
    min_num = 0
    max_num = 10


class AssortmentImageInline(admin.TabularInline):
    model = AssortmentImage
    extra = 1
    verbose_name = "Зображення"
    verbose_name_plural = "Галерея зображень"
    readonly_fields = ['preview']

    def preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 100px;">')
        return ""
    preview.short_description = "Превʼю"


@admin.register(Assortment)
class AssortmentAdmin(admin.ModelAdmin):
    form = AssortmentAdminForm

    list_display = ['preview', 'assortment_name', 'get_categories', 'producer', 'price', 'old_price', 'is_discounted', 'is_available']
    list_filter = ['producer', 'is_available', 'is_discounted']
    search_fields = ['assortment_name']
    inlines = [AssortmentImageInline, AssortmentVariantInline]
    filter_horizontal = ['filters', 'tags', 'assortment_categories']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Основна інформація', {
            'fields': (
                'assortment_name', 'poster', 'assortment_description',
                'assortment_categories', 'filters', 'tags', 'producer'
            )
        }),
        ('Ціни та доступність', {
            'fields': (
                'price', 'old_price', 'grams',
                'is_available', 'is_discounted', 'has_variants'
            )
        }),
        ('Інше', {
            'fields': ('popularity', 'created_at')
        }),
    )

    def get_categories(self, obj):
        return ", ".join([cat.category for cat in obj.assortment_categories.all()])
    get_categories.short_description = 'Категорії'

    def preview(self, obj):
        if obj.poster:
            return format_html('<img src="{}" style="max-height: 80px;" />', obj.poster.url)
        return "-"
    preview.short_description = 'Зображення'

    def save_model(self, request, obj, form, change):
        if not obj.has_variants and obj.old_price:
            obj.is_discounted = True
        super().save_model(request, obj, form, change)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category']
    search_fields = ['category']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(FilterGroup)
class FilterGroupAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(FilterOption)
class FilterOptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'group']
    list_filter = ['group']
    search_fields = ['name']
