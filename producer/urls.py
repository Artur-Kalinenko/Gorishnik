from django.urls import path
from . import views
from assortment.views import assortment_list

urlpatterns = [
    path('', views.producer_list, name='producer_list'),
    path('assortment/producer/<slug:producer_slug>/', assortment_list, name='producer_detail'),
]