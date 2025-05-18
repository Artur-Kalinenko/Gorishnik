from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from assortment import views as assortment_views
from cart.views import add_to_cart, remove_from_cart, cart_view, update_quantity, checkout_view, order_payment_view, liqpay_callback_view, checkout_done_view, clear_guest_cart
from accounts.views import (
    register_view, login_view, logout_view,
    password_reset_request_view,
    password_reset_code_view,
    password_reset_new_password_view,
    verify_email_view,
    user_cabinet_view,
    edit_profile_view,
    google_login_complete_safe
)


urlpatterns = [
    # Админка
    path('admin/', admin.site.urls),

    # Приложения
    path('assortment/', include('assortment.urls')),
    path('producer/', include('producer.urls')),

    # Главная и информационные страницы
    path('', assortment_views.welcome, name='welcome'),
    path('reviews/', assortment_views.reviews, name='reviews'),
    path('delivery/', assortment_views.delivery, name='delivery'),

    # Корзина
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/update_quantity/<int:item_id>/', update_quantity, name='update_quantity'),
    path('cart/', cart_view, name='cart'),
    path('checkout/', checkout_view, name='checkout'),
    path('order/<int:order_id>/pay/', order_payment_view, name='order_payment'),
    path('liqpay-callback/', liqpay_callback_view, name='liqpay_callback'),
    path('checkout/done/', checkout_done_view, name='checkout_done'),

    path('clear-session/', clear_guest_cart, name='clear_guest_cart'),

    # Аутентификация
    path('register/', register_view, name='register'),
    path('verify-email/', verify_email_view, name='verify_email'),
    path('auth/complete/<str:backend>/', google_login_complete_safe, name='google_complete'),
    path('auth/', include('social_django.urls', namespace='social')),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Сброс пароля
    path('password-reset/', password_reset_request_view, name='password_reset_request'),
    path('password-reset/verify/', password_reset_code_view, name='password_reset_code'),
    path('password-reset/set-new/', password_reset_new_password_view, name='set_new_password'),

    # Кабинет юзера
    path('cabinet/', user_cabinet_view, name='user_cabinet'),
    path('cabinet/edit/', edit_profile_view, name='edit_profile'),
]

# Медиа в режиме отладки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
