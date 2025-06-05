from django.urls import path
from . import views

urlpatterns = [
    path('assortment/', views.category_list_view, name='assortment_list'),  # список категорий
    path('assortment/items/', views.assortment_list, name='assortment_items'),  # список товаров
    path('assortment/<int:pk>/', views.assortment_detail, name='assortment_detail'),  # детальная карточка
    path('assortment/search_suggest/', views.search_suggest, name='search_suggest'),
    path('assortment/review/<int:review_id>/delete/', views.delete_review_view, name='delete_review'),
]
