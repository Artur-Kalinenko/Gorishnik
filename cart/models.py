from django.db import models
from assortment.models import Assortment, AssortmentVariant
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone

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
        price = self.variant.price if self.variant else self.product.price
        return (price or 0) * self.quantity

    # Общий вес
    def total_grams(self):
        if self.variant:
            return self.variant.grams * self.quantity
        return self.product.grams * self.quantity

    def __str__(self):
        return f"{self.product.assortment_name} x {self.quantity}"
