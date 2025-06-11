from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.shortcuts import redirect

def redirect_to_uk(request):
    # Получаем язык из cookie или используем язык по умолчанию
    language = request.COOKIES.get('django_language', settings.LANGUAGE_CODE)
    return redirect(f'/{language}/')

urlpatterns = [
    path('', redirect_to_uk),
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('assortment/', include('assortment.urls')),
    path('producer/', include('producer.urls')),
    path('cart/', include('cart.urls')),
    path('order/', include('orders.urls')),
    path('delivery/', include('delivery.urls')),
    path('payment/', include('payments.urls')),
    path('favorites/', include('favorites.urls')),
    path('', include('accounts.urls')),
    path('', include('pages.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)