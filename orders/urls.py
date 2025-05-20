from django.urls import path
from .views import checkout_view

urlpatterns = [
    path('checkout/', checkout_view, name='checkout'),
]