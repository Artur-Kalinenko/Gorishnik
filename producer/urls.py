from django.urls import path
from . import views

urlpatterns = [
    path('', views.producer_list, name='producer_list'),
]