from cart.models import Cart, CartItem

# Помечает пользователя как верифицированного после успешной авторизации через соцсеть
def set_verified(backend, user, *args, **kwargs):
    if user and not user.is_verified:
        user.is_verified = True
        user.save()

#мердж корзины после логина
def transfer_guest_cart(backend, strategy, request=None, user=None, *args, **kwargs):
    if user is None:
        return

    session_key = strategy.session_get('pre_social_auth_session_key') or strategy.session.session_key
    if not session_key:
        return

    # Ищем корзину гостя
    guest_cart = Cart.objects.filter(session_id=session_key, user__isnull=True).first()
    if not guest_cart:
        return

    # Получаем или создаём корзину пользователя
    user_cart = Cart.objects.filter(user=user).first()
    if not user_cart:
        guest_cart.user = user
        guest_cart.session_id = None  # больше не нужна
        guest_cart.save()
        return

    # Объединяем товары из guest_cart в user_cart
    for item in guest_cart.items.all():
        existing = user_cart.items.filter(product=item.product, variant=item.variant).first()
        if existing:
            existing.quantity += item.quantity
            existing.save()
            item.delete()
        else:
            item.cart = user_cart
            item.save()
    guest_cart.delete()