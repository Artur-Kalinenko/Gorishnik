from django.contrib import admin
from .models import Assortment, AssortmentVariant, Category


# Варианты (граммовки) отображаются прямо внутри товара
class AssortmentVariantInline(admin.TabularInline):
    model = AssortmentVariant
    extra = 1
    fields = ['grams', 'price']
    min_num = 0
    max_num = 10

# Админка для модели Assortment
@admin.register(Assortment)
class AssortmentAdmin(admin.ModelAdmin):
    list_display = ['assortment_name', 'assortment_categories', 'is_available', 'producer']
    list_filter = ['assortment_categories', 'is_available', 'producer']
    search_fields = ['assortment_name']
    inlines = [AssortmentVariantInline]

# Админка для категорий
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category']
    search_fields = ['category']
