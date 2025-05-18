from django.core.management.base import BaseCommand
from cart.models import Cart, CartItem
from datetime import timedelta
from django.utils import timezone


# Команда для удаления устаревших корзин и товаров из корзин
class Command(BaseCommand):
    help = 'Удаляет старые корзины и их товары'

    def handle(self, *args, **kwargs):
        now = timezone.now()

        # Удаляем товары из корзин, не обновлявшиеся более 24 часов
        threshold_items = now - timedelta(hours=24)
        deleted_items, _ = CartItem.objects.filter(updated_at__lt=threshold_items).delete()

        # Удаляем корзины гостей, которые не обновлялись более 2 дней
        threshold_guest = now - timedelta(days=2)
        deleted_guest_carts, _ = Cart.objects.filter(
            user__isnull=True,
            updated_at__lt=threshold_guest
        ).delete()

        # Удаляем корзины авторизованных пользователей, не обновлявшиеся более 30 дней
        threshold_users = now - timedelta(days=30)
        deleted_user_carts, _ = Cart.objects.filter(
            user__isnull=False,
            updated_at__lt=threshold_users
        ).delete()

        # Выводим информацию о количестве удалённых объектов
        self.stdout.write(
            f"Удалено товаров: {deleted_items}, "
            f"корзин гостей: {deleted_guest_carts}, "
            f"корзин пользователей: {deleted_user_carts}"
        )
