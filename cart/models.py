from django.db import models
from assortment.models import Assortment, AssortmentVariant
from django.conf import settings

# Модель корзины: может быть привязана к пользователю или session_id
class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Корзина {self.user or self.session_id}"

# Позиция в корзине (товар + количество + вариант, если есть)
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Assortment, on_delete=models.CASCADE)
    variant = models.ForeignKey(
        'assortment.AssortmentVariant',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Варіант продукту'
    )
    quantity = models.PositiveIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    # Общая сумма за этот товар
    def total_price(self):
        price = self.variant.price if self.variant else self.product.price
        return (price or 0) * self.quantity

    # Общий вес (в граммах)
    def total_grams(self):
        if self.variant:
            return self.variant.grams * self.quantity
        return self.product.grams * self.quantity

    def __str__(self):
        variant_info = f" ({self.total_grams()}г)" if self.variant else ""
        return f"{self.quantity} x {self.product.assortment_name}{variant_info}"

