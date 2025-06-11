from modeltranslation.translator import translator, TranslationOptions
from .models import Assortment, Category, FilterGroup, FilterOption, Tag

class AssortmentTranslationOptions(TranslationOptions):
    fields = ('assortment_name', 'assortment_description',)

class CategoryTranslationOptions(TranslationOptions):
    fields = ('category',)

class FilterGroupTranslationOptions(TranslationOptions):
    fields = ('name',)

class FilterOptionTranslationOptions(TranslationOptions):
    fields = ('name',)

class TagTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(Assortment, AssortmentTranslationOptions)
translator.register(Category, CategoryTranslationOptions)
translator.register(FilterGroup, FilterGroupTranslationOptions)
translator.register(FilterOption, FilterOptionTranslationOptions)
translator.register(Tag, TagTranslationOptions)
