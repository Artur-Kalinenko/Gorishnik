from django.urls import path
from .views import (
    add_to_cart, remove_from_cart, update_quantity, cart_view,
    checkout_view, order_payment_view, liqpay_callback_view,
    checkout_done_view, clear_guest_cart,
)

urlpatterns = [
    # Просмотр корзины
    path('', cart_view, name='cart'),

    # Управление товарами в корзине
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('update_quantity/<int:item_id>/', update_quantity, name='update_quantity'),

    # Оформление и оплата заказа
    path('checkout/', checkout_view, name='checkout'),
    path('checkout/done/', checkout_done_view, name='checkout_done'),
    path('order/<int:order_id>/pay/', order_payment_view, name='order_payment'),
    path('liqpay-callback/', liqpay_callback_view, name='liqpay_callback'),

    # Очистка корзины гостей
    path('clear-session/', clear_guest_cart, name='clear_guest_cart'),
]
