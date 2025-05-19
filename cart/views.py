from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Cart, CartItem, Order, OrderItem
from assortment.models import Assortment, AssortmentVariant
from django.core.mail import send_mail
from django.conf import settings
from .forms import OrderForm
from cart.liqpay_client import LiqPay
from accounts.forms import LoginForm
import json
import base64
from django.views.decorators.http import require_POST


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

        return JsonResponse({
            'message': 'Продукт добавлен в корзину!',
            'total_items': cart.items.count(),
            'session_id': cart.session_id
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

            return JsonResponse({
                'success': True,
                'item_total_price': cart_item.total_price(),
                'cart_total_price': cart_total_price,
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

        cart = cart_item.cart
        cart_total_price = sum(item.total_price() for item in cart.items.all())

        return JsonResponse({
            'success': True,
            'cart_total_price': cart_total_price,
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

    return {
        'cart': cart,
        'login_form': LoginForm()
    }

# Оформление заказа + отправка email + очистка корзины
def checkout_view(request):
    cart = get_or_create_cart(request)
    items = cart.items.all()

    if not items:
        return render(request, 'cart/checkout.html', {
            'error': 'Кошик порожній'
        })

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                full_name=cd['full_name'],
                phone=cd['phone'],
                email=cd['email'],
                delivery_method=cd['delivery_method'],
                address=cd['address'],
            )

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    variant=item.variant,
                    quantity=item.quantity
                )

            subject = 'Нове замовлення з сайту'
            # Формируем список товаров
            items_text = ""
            for item in items:
                name = item.product.assortment_name if item.product else "Невідомий товар"
                grams = item.variant.grams if item.variant else (item.product.grams if item.product else "-")
                price = item.variant.price if item.variant else (item.product.price if item.product else 0)
                quantity = item.quantity
                total = price * quantity
                items_text += f"- {name} — {grams}г × {quantity} = {total} грн\n"

            message = f"""
            Нове замовлення

            ПІБ: {cd['full_name']}
            Телефон: {cd['phone']}
            Email: {cd['email']}
            Спосіб доставки: {cd['delivery_method']}
            Адреса: {cd['address']}

            Замовлені товари:
            {items_text}
            Загальна сума: {order.total_price()} грн
            """
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                ['kalinenko.a01@gmail.com'],
                fail_silently=False
            )

            cart.items.all().delete()
            return redirect('order_payment', order_id=order.id)

    else:
        form = OrderForm()

    return render(request, 'cart/checkout.html', {
        'form': form,
        'items': items,
        'total_price': sum(i.total_price() for i in items)
    })


# Страница оплаты через LiqPay — генерация подписи и данных
def order_payment_view(request, order_id):
    order = Order.objects.get(id=order_id)

    liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)

    params = {
        'action': 'pay',
        'amount': order.total_price(),
        'currency': 'UAH',
        'description': f'Оплата замовлення №{order.id}',
        'order_id': str(order.id),
        'version': '3',
        'sandbox': 1 if getattr(settings, 'LIQPAY_SANDBOX', True) else 0,
        'server_url': request.build_absolute_uri('/liqpay-callback/'),
        'result_url': request.build_absolute_uri('/cart/checkout/done/'),
        'fail_url': request.build_absolute_uri('/cart/checkout/failed/'),
    }

    data = liqpay.cnb_data(params)
    signature = liqpay.cnb_signature(params)

    return render(request, 'cart/liqpay_payment.html', {
        'order': order,
        'data': data,
        'signature': signature
    })

# Обработка callback-а от LiqPay (POST-запрос с результатом оплаты)
@csrf_exempt
def liqpay_callback_view(request):
    data = request.POST.get('data')
    signature = request.POST.get('signature')

    liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)

    if signature == liqpay.str_to_sign(
        settings.LIQPAY_PRIVATE_KEY + data + settings.LIQPAY_PRIVATE_KEY
    ):
        decoded_data = json.loads(base64.b64decode(data).decode('utf-8'))
        order_id = decoded_data.get('order_id')
        status = decoded_data.get('status')

        if order_id and status in ['success', 'sandbox']:
            order = Order.objects.filter(id=order_id).first()
            if order:
                order.payment_status = 'paid'
                order.save()

    return HttpResponse("OK")


# Завершение оформления — отображается после успешной оплаты
def checkout_done_view(request):
    return render(request, 'cart/checkout_done.html')

# Отображается после неудачной оплаты
def checkout_failed_view(request):
    return render(request, 'cart/checkout_failed.html')

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
