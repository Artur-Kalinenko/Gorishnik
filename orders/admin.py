from django.contrib import admin
from .models import Order, OrderItem

# Инлайн-товары в заказе (удобно для просмотра из Order)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = ['product', 'variant', 'get_grams', 'get_price', 'quantity', 'get_total']
    verbose_name = 'Товар в замовленні'
    verbose_name_plural = 'Список товарів'

    def get_price(self, obj):
        return f"{obj.variant.price if obj.variant else obj.product.price if obj.product else '-'} ₴"
    get_price.short_description = 'Ціна за одиницю'

    def get_grams(self, obj):
        return f"{obj.variant.grams if obj.variant else obj.product.grams if obj.product else '-'} г"
    get_grams.short_description = 'Грамовка'

    def get_total(self, obj):
        return f"{obj.total_price()} ₴"
    get_total.short_description = 'Разом'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'phone', 'email', 'delivery_method', 'created_at', 'get_total_price', 'payment_status')
    list_filter = ('delivery_method', 'created_at', 'payment_status')
    search_fields = ('full_name', 'email', 'phone')
    readonly_fields = ['created_at']
    inlines = [OrderItemInline]

    def get_total_price(self, obj):
        return f"{obj.total_price()} ₴"
    get_total_price.short_description = 'Сума'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'variant', 'get_grams', 'get_price', 'quantity', 'get_total')
    readonly_fields = ['order', 'product', 'variant', 'quantity', 'get_grams', 'get_price', 'get_total']

    def get_price(self, obj):
        return f"{obj.variant.price if obj.variant else obj.product.price if obj.product else '-'} ₴"
    get_price.short_description = 'Ціна'

    def get_grams(self, obj):
        return f"{obj.variant.grams if obj.variant else obj.product.grams if obj.product else '-'} г"
    get_grams.short_description = 'Грамовка'

    def get_total(self, obj):
        return f"{obj.total_price()} ₴"
    get_total.short_description = 'Разом'

