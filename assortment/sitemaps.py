from django.contrib.sitemaps import Sitemap
from .models import Assortment, Category
from producer.models import Producer

class AssortmentSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Assortment.objects.filter(is_available=True)

    def location(self, obj):
        return obj.get_absolute_url()

class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()

class ProducerSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Producer.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()
