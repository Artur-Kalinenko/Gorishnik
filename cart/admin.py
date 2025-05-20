from django.contrib import admin
from .models import Cart, CartItem


# Админка для корзин
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_id', 'created_at')
    search_fields = ('user__email', 'session_id')
    list_filter = ('created_at',)


# Админка для товаров в корзине
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'variant', 'quantity')
    list_filter = ('cart', 'product')
