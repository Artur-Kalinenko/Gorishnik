from django.db import models
from django.conf import settings
from assortment.models import Assortment, AssortmentVariant

# Модель заказа (в т.ч. для гостей)
class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    delivery_method = models.CharField(max_length=50)
    address = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Статус оплаты
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Очікується'),
            ('paid', 'Оплачено'),
            ('failed', 'Не вдалося'),
        ],
        default='pending'
    )

    # Общая сумма по заказу
    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

    def __str__(self):
        return f"Замовлення №{self.id} — {self.full_name}"

# Позиция в заказе (аналог CartItem)
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Assortment, on_delete=models.SET_NULL, null=True)
    variant = models.ForeignKey(AssortmentVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()

    # Общая сумма по позиции
    def total_price(self):
        price = None
        if self.variant and self.variant.price is not None:
            price = self.variant.price
        elif self.product and self.product.price is not None:
            price = self.product.price
        else:
            price = 0
        return price * self.quantity

    # Общий вес
    def total_grams(self):
        if self.variant and self.variant.grams is not None:
            return self.variant.grams * self.quantity
        elif self.product and self.product.grams is not None:
            return self.product.grams * self.quantity
        return 0

    def __str__(self):
        name = self.product.assortment_name if self.product else "Невідомий продукт"
        grams = self.total_grams()
        return f"{name} x {self.quantity} ({grams} г)"

