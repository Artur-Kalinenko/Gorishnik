from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Cart, CartItem
from assortment.models import Assortment, AssortmentVariant
from accounts.forms import LoginForm
import json
from django.views.decorators.http import require_POST
from django.db.models import Sum


# Получить корзину пользователя или гостя (по session_id), либо создать новую
def get_or_create_cart(request):
    if request.user.is_authenticated:
        return Cart.objects.filter(user=request.user).first() or Cart.objects.create(user=request.user)
    else:
        session_id = request.session.session_key or request.session.create()
        return Cart.objects.filter(session_id=session_id).first() or Cart.objects.create(session_id=session_id)


# Добавление товара в корзину (через fetch или JS POST)
@csrf_exempt
def add_to_cart(request, product_id):
    if request.method == 'POST':
        cart = get_or_create_cart(request)
        product = get_object_or_404(Assortment, id=product_id)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = request.POST

        variant_id = data.get('variant_id')
        variant_id = int(variant_id) if variant_id not in [None, '', 'null', 'undefined'] else None
        quantity = int(data.get('quantity', 1))

        if variant_id:
            variant = get_object_or_404(AssortmentVariant, id=variant_id, assortment=product)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, product=product, variant=variant
            )
        else:
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, product=product, variant=None
            )

        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity

        cart_item.save()

        total_quantity = cart.items.aggregate(total=Sum('quantity'))['total'] or 0

        return JsonResponse({
            'status': 'success',
            'message': 'Продукт додано в кошик!',
            'cart_item_count': total_quantity
        })

    return JsonResponse({'error': 'Неверный запрос'}, status=400)


# Обновление количества товара в корзине
@csrf_exempt
def update_quantity(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id)
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))

        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()

            cart = cart_item.cart
            cart_total_price = sum(item.total_price() for item in cart.items.all())

            cart_total_quantity = cart.items.aggregate(total=Sum('quantity'))['total'] or 0

            return JsonResponse({
                'success': True,
                'item_total_price': cart_item.total_price(),
                'cart_total_price': cart_total_price,
                'cart_total_quantity': cart_total_quantity,
            })
        else:
            return JsonResponse({'success': False, 'message': 'Количество должно быть больше 0'})

    return JsonResponse({'success': False, 'message': 'Неверный запрос'})


# Объединение дублирующихся товаров в корзине (по продукту и варианту)
def merge_cart_items(cart):
    items = cart.items.all()
    merged = {}

    for item in items:
        key = (item.product.id, item.variant.id if item.variant else None)
        if key in merged:
            existing_item = merged[key]
            existing_item.quantity += item.quantity
            existing_item.save()
            item.delete()
        else:
            merged[key] = item


# Удаление товара из корзины
def remove_from_cart(request, item_id):
    if request.method == 'POST':
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.delete()

        # Пересчитываем корзину уже после удаления
        cart_total_price = sum(item.total_price() for item in cart.items.all())
        cart_total_quantity = cart.items.aggregate(total=Sum('quantity'))['total'] or 0

        return JsonResponse({
            'success': True,
            'cart_total_price': cart_total_price,
            'cart_total_quantity': cart_total_quantity,
        })

    return JsonResponse({'success': False, 'message': 'Неверный запрос'})


# Отображение содержимого корзины
def cart_view(request):
    cart = get_or_create_cart(request)
    items = cart.items.all()
    total_price = sum(item.total_price() for item in items)

    return render(request, 'cart/cart.html', {
        'cart': cart,
        'items': items,
        'total_price': total_price,
    })


# Контекст корзины для base.html (отдельно вызывается в `context_processors`)
def base_context(request):
    session_id = request.session.session_key or request.session.create()

    if request.user.is_authenticated:
        # Ищем только корзины текущего пользователя
        carts = Cart.objects.filter(user=request.user)
    else:
        # Только корзины без пользователя
        carts = Cart.objects.filter(session_id=session_id, user__isnull=True)

    if carts.count() > 1:
        main_cart = carts.first()
        for extra_cart in carts.exclude(id=main_cart.id):
            for item in extra_cart.items.all():
                existing = main_cart.items.filter(
                    product=item.product,
                    variant=item.variant
                ).first()
                if existing:
                    existing.quantity += item.quantity
                    existing.save()
                else:
                    item.cart = main_cart
                    item.save()
            extra_cart.delete()
        cart = main_cart
    else:
        cart = carts.first() if carts.exists() else None

    total_quantity = 0
    if cart:
        total_quantity = cart.items.aggregate(total=Sum('quantity'))['total'] or 0

    return {
        'cart': cart,
        'cart_total_quantity': total_quantity,
        'login_form': LoginForm()
    }


# Очистка корзины гостя по session_id (вызов из JS при истечении срока)
@require_POST
@csrf_exempt  # если используется fetch с CSRF, можно убрать
def clear_guest_cart(request):
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')

        if session_id:
            Cart.objects.filter(user__isnull=True, session_id=session_id).delete()
            return JsonResponse({'status': 'ok'})
        return JsonResponse({'status': 'error', 'message': 'session_id missing'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
