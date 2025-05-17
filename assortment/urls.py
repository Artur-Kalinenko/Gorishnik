from django.urls import path
from . import views

urlpatterns = [
    path('', views.assortment_list, name='assortment_list'),
    path('<int:pk>/', views.assortment_detail, name='assortment_detail'),
]
