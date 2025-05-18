from django.urls import path, include
from .views import welcome, reviews, delivery

urlpatterns = [
    path('', welcome, name='welcome'),             # Главная
    path('reviews/', reviews, name='reviews'),     # Отзывы
    path('delivery/', delivery, name='delivery'),  # Доставка
]