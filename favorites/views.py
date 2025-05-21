from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from .models import Favorite
from assortment.models import Assortment

@login_required
def toggle_favorite(request, product_id):
    product = get_object_or_404(Assortment, id=product_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)

    if not created:
        favorite.delete()
        return JsonResponse({'status': 'removed'})
    return JsonResponse({'status': 'added'})

@login_required
def favorite_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('product')
    favorites_ids = list(favorites.values_list('product_id', flat=True))

    return render(request, 'favorites/favorite_list.html', {
        'favorites': favorites,
        'favorites_ids': favorites_ids,
    })
