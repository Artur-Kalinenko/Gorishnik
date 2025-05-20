from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from orders.models import Order, OrderItem
from cart.views import get_or_create_cart
from .forms import OrderForm

def checkout_view(request):
    cart = get_or_create_cart(request)
    items = cart.items.all()

    if not items:
        return render(request, 'orders/checkout.html', {
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

    return render(request, 'orders/checkout.html', {
        'form': form,
        'items': items,
        'total_price': sum(i.total_price() for i in items)
    })
