from django.urls import path
from .views import toggle_favorite, favorite_list

urlpatterns = [
    path('toggle/<int:product_id>/', toggle_favorite, name='toggle_favorite'),
    path('list/', favorite_list, name='favorite_list'),
]