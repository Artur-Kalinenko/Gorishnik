from django.urls import path
from . import views

urlpatterns = [
    path('', views.category_list_view, name='category_list'),  # список категорий
    path('assortment/', views.assortment_list, name='assortment_list'),  # список товаров
    path('assortment/category/<slug:slug>/', views.assortment_list, name='category_detail'),
    path('assortment/<slug:slug>/', views.assortment_detail, name='assortment_detail'),  # детальная карточка
    path('search_suggest/', views.search_suggest, name='search_suggest'),
    path('review/<int:review_id>/delete/', views.delete_review_view, name='delete_review'),
]