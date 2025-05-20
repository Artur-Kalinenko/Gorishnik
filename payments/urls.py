from django.urls import path
from .views import (
    order_payment_view,
    liqpay_callback_view,
    checkout_done_view,
    checkout_failed_view
)

urlpatterns = [
    path('liqpay/<int:order_id>/', order_payment_view, name='order_payment'),
    path('liqpay-callback/', liqpay_callback_view, name='liqpay_callback'),
    path('checkout/done/', checkout_done_view, name='checkout_done'),
    path('checkout/failed/', checkout_failed_view, name='checkout_failed'),
]