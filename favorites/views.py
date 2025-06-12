from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from functools import wraps
from .models import Favorite
from assortment.models import Assortment

def ajax_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'login_required'}, status=403)
            return login_required(view_func)(request, *args, **kwargs)
        return view_func(request, *args, **kwargs)
    return wrapper

@ajax_login_required
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
