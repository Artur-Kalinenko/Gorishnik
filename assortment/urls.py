from django.urls import path
from . import views

urlpatterns = [
    path('', views.assortment_list, name='assortment_list'), # Список товаров
    path('<int:pk>/', views.assortment_detail, name='assortment_detail'), # Детальная страница товара
]
