from django.urls import path
from .views import (
    add_to_cart, remove_from_cart, update_quantity, cart_view,
    clear_guest_cart
)

urlpatterns = [
    # Просмотр корзины
    path('', cart_view, name='cart'),

    # Управление товарами в корзине
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('update_quantity/<int:item_id>/', update_quantity, name='update_quantity'),

    # Очистка корзины гостей
    path('clear-session/', clear_guest_cart, name='clear_guest_cart'),
]

