from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from payments.liqpay_client import LiqPay
from orders.models import Order
import json
import base64

# Страница оплаты через LiqPay — генерация подписи и данных
def order_payment_view(request, order_id):
    order = Order.objects.get(id=order_id)

    liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)

    params = {
        'action': 'pay',
        'amount': float(order.total_price()),
        'currency': 'UAH',
        'description': f'Оплата замовлення №{order.id}',
        'order_id': str(order.id),
        'version': '3',
        'sandbox': 1 if getattr(settings, 'LIQPAY_SANDBOX', True) else 0,
        'server_url': request.build_absolute_uri('/payment/liqpay-callback/'),
        'result_url': request.build_absolute_uri('/payment/checkout/done/'),
        'fail_url': request.build_absolute_uri('/payment/checkout/failed/'),
    }

    data = liqpay.cnb_data(params)
    signature = liqpay.cnb_signature(params)

    print("=== LIQPAY PARAMS ===")
    for k, v in params.items():
        print(f"{k}: {v}")
    print("=== TOTAL:", order.total_price())
    return render(request, 'payments/liqpay_payment.html', {
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
    return render(request, 'payments/checkout_done.html')

# Отображается после неудачной оплаты
def checkout_failed_view(request):
    return render(request, 'payments/checkout_failed.html')