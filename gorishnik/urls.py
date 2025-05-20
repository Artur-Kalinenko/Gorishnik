from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Админка
    path('admin/', admin.site.urls),

    # Приложения
    path('assortment/', include('assortment.urls')),
    path('producer/', include('producer.urls')),
    path('cart/', include('cart.urls')),
    path('order/', include('orders.urls')),
    path('delivery/', include('delivery.urls')),
    path('payment/', include('payments.urls')),
    path('', include('accounts.urls')),
    path('', include('pages.urls')),
]

# Медиафайлы в режиме DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)