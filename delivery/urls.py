from django.urls import path
from . import views

urlpatterns = [
    path("city-autocomplete/", views.city_autocomplete, name="city_autocomplete"),
    path("warehouse-autocomplete/", views.warehouse_autocomplete, name="warehouse_autocomplete"),
]