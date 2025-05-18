from django.contrib import admin

from .models import Order, OrderItem, Cart, CartItem

# Инлайн-отображение товаров в заказе (для Order)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

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

# Админка для заказов
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'phone', 'email', 'delivery_method', 'created_at')
    list_filter = ('delivery_method', 'created_at')
    search_fields = ('full_name', 'email', 'phone')
    inlines = [OrderItemInline]

# Админка для отдельных товаров в заказе (опционально)
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'variant', 'quantity')
