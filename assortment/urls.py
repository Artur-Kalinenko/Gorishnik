from django.urls import path
from . import views
from .views import search_suggest, delete_review_view

urlpatterns = [
    path('', views.assortment_list, name='assortment_list'), # Список товаров
    path('<int:pk>/', views.assortment_detail, name='assortment_detail'), # Детальная страница товара
    path('search_suggest/', search_suggest, name='search_suggest'), # AJAX

    path('review/<int:review_id>/delete/', delete_review_view, name='delete_review'),
]
