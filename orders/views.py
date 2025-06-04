from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from orders.models import Order, OrderItem
from cart.views import get_or_create_cart
from .forms import OrderForm
from delivery.np_api import np_request  # импорт для запроса к Новой Поште

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
            delivery_method = cd['delivery_method']
            payment_method = cd['payment_method']

            address = ''
            city_ref = None
            warehouse_ref = None
            city_name = "-"
            warehouse_name = "-"

            if delivery_method == 'nova_poshta':
                city_ref = request.POST.get('city_ref')
                warehouse_ref = request.POST.get('warehouse_ref')
                address = "Нова Пошта"

                # Название города
                if city_ref:
                    resp = np_request("Address", "getCities", {"Ref": city_ref})
                    if resp.get("success") and resp.get("data"):
                        city_name = resp["data"][0]["Description"]

                # Название отделения
                if warehouse_ref:
                    resp = np_request("AddressGeneral", "getWarehouses", {"Ref": warehouse_ref})
                    if resp.get("success") and resp.get("data"):
                        warehouse_name = resp["data"][0]["Description"]

            elif delivery_method == 'ukr_poshta':
                ukr_city = request.POST.get('ukr_city')
                ukr_address = request.POST.get('ukr_address')
                address = f"Укрпошта: {ukr_city}, {ukr_address}"

            elif delivery_method == 'pickup':
                address = 'Самовивіз'

            additional_notes = cd.get('additional_notes', '')

            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                full_name=cd['full_name'],
                phone=cd['phone'],
                email=cd['email'],
                delivery_method=delivery_method,
                address=address,
                city_ref=city_ref,
                warehouse_ref=warehouse_ref,
            )

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    variant=item.variant,
                    quantity=item.quantity
                )

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
Спосіб доставки: {delivery_method}
Адреса: {address}
Місто (НП): {city_name}
Відділення (НП): {warehouse_name}

Спосіб оплати: {dict(form.fields['payment_method'].choices).get(payment_method, '')}

Додаткові побажання: {additional_notes}

Замовлені товари:
{items_text}
Загальна сума: {order.total_price()} грн
            """

            send_mail(
                subject='Нове замовлення з сайту',
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['kalinenko.a01@gmail.com'],
                fail_silently=False
            )

            cart.items.all().delete()
            if payment_method == 'cod':
                return redirect('order_success', order_id=order.id)
            elif payment_method == 'online':
                return redirect('order_payment', order_id=order.id)
            elif payment_method == 'invoice':
                return redirect('order_invoice', order_id=order.id)

    else:
        form = OrderForm()

    return render(request, 'orders/checkout.html', {
        'form': form,
        'items': items,
        'total_price': sum(i.total_price() for i in items)
    })
