from django.urls import path
from .views import (
    order_payment_view,
    liqpay_callback_view,
    checkout_done_view,
    checkout_failed_view,
    order_success_view,
    order_invoice_view,
)

urlpatterns = [
    path('liqpay/<int:order_id>/', order_payment_view, name='order_payment'),
    path('success/<int:order_id>/', order_success_view, name='order_success'),
    path('invoice/<int:order_id>/', order_invoice_view, name='order_invoice'),
    path('liqpay-callback/', liqpay_callback_view, name='liqpay_callback'),
    path('checkout/done/', checkout_done_view, name='checkout_done'),
    path('checkout/failed/', checkout_failed_view, name='checkout_failed'),
]