from django.db import models

# Модель для хранения изготовителя
class Producer(models.Model):
    producer_name = models.CharField(max_length=100, verbose_name='Назва виробника')
    producer_img = models.ImageField(upload_to='producer/posters/', null=True, blank=True, verbose_name='Логотип Виробника')

    def __str__(self):
        return self.producer_name

    class Meta:
        verbose_name = 'Виробник'
        verbose_name_plural = 'Виробники'
        ordering = ['producer_name']