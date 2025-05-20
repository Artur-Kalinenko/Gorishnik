from django.contrib import admin
from .models import Assortment, AssortmentVariant, Category, FilterGroup, FilterOption, Tag
from producer.models import Producer

# Варианты (граммовки) отображаются прямо внутри товара
class AssortmentVariantInline(admin.TabularInline):
    model = AssortmentVariant
    extra = 1
    fields = ['grams', 'price']
    min_num = 0
    max_num = 10

# Админка для модели Assortment (товар)
@admin.register(Assortment)
class AssortmentAdmin(admin.ModelAdmin):
    list_display = ['assortment_name', 'assortment_categories', 'producer', 'price', 'is_available']
    list_filter = ['assortment_categories', 'producer', 'is_available']
    search_fields = ['assortment_name']
    inlines = [AssortmentVariantInline]
    filter_horizontal = ['filters', 'tags']


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
