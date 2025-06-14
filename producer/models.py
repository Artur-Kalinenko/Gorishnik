from django.db import models
from django.urls import reverse
from django.utils.text import slugify

# Модель для хранения изготовителя
class Producer(models.Model):
    producer_name = models.CharField(max_length=100, verbose_name='Назва виробника')
    producer_img = models.ImageField(upload_to='producer/posters/', null=True, blank=True, verbose_name='Логотип Виробника')
    slug = models.SlugField(max_length=100, unique=True, blank=True, verbose_name="Slug")

    def __str__(self):
        return self.producer_name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.producer_name)
            slug = base_slug
            num = 1
            while Producer.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('producer_detail', args=[self.slug])

    class Meta:
        verbose_name = 'Виробник'
        verbose_name_plural = 'Виробники'
        ordering = ['producer_name']