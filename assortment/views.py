from django.shortcuts import render, get_object_or_404, redirect
from django.db.models.expressions import OrderBy
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import Q, Prefetch, Count, Case, When, F, Subquery, OuterRef, DecimalField, Avg
from django.contrib.auth.decorators import login_required
from .models import (
    Assortment, Category,
    AssortmentVariant, FilterGroup, FilterOption, Review
)
from .forms import ReviewForm
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from datetime import timedelta


def assortment_list(request):
    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    selected_filter_ids = list(map(int, request.GET.getlist('filters')))
    query = request.GET.get('q', '')
    sort = request.GET.get('sort')
    discounted_only = request.GET.get('discounted') == '1'
    new_only = request.GET.get('new') == '1'
    my_favorites_only = request.GET.get('my_favorites') == '1'

    assortments = Assortment.objects.all()
    current_category = None

    if selected_category:
        assortments = assortments.filter(assortment_categories__category=selected_category)
        current_category = categories.filter(category=selected_category).first()

    if selected_filter_ids:
        for filter_id in selected_filter_ids:
            assortments = assortments.filter(filters__id=filter_id)

    if discounted_only:
        assortments = assortments.filter(is_discounted=True)

    if new_only:
        assortments = assortments.filter(created_at__gte=timezone.now() - timezone.timedelta(days=30))

    if my_favorites_only and request.user.is_authenticated:
        from favorites.models import Favorite
        favorite_ids = Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)
        assortments = assortments.filter(id__in=favorite_ids)

    if query:
        assortments = assortments.filter(
            Q(assortment_name__icontains=query) |
            Q(assortment_description__icontains=query) |
            Q(assortment_categories__category__icontains=query) |
            Q(tags__name__icontains=query) |
            Q(filters__name__icontains=query) |
            Q(filters__group__name__icontains=query)
        ).distinct()

    variant_qs = AssortmentVariant.objects.filter(assortment=OuterRef('pk'))

    if sort == 'price_desc':
        price_subquery = Subquery(variant_qs.order_by('-price').values('price')[:1])
    else:
        price_subquery = Subquery(variant_qs.order_by('price').values('price')[:1])

    assortments = assortments.annotate(
        effective_price=Case(
            When(variants__isnull=False, then=price_subquery),
            default=F('price'),
            output_field=DecimalField()
        ),
        min_price=Subquery(variant_qs.order_by('price').values('price')[:1], output_field=DecimalField()),
        max_price=Subquery(variant_qs.order_by('-price').values('price')[:1], output_field=DecimalField()),
        avg_rating=Avg('reviews__rating'),
    ).prefetch_related('variants').distinct()

    if sort == 'price_asc':
        assortments = assortments.order_by('effective_price')
    elif sort == 'price_desc':
        assortments = assortments.order_by('-effective_price')
    elif sort == 'newest':
        assortments = assortments.order_by('-created_at')
    elif sort == 'popular':
        assortments = assortments.order_by('-popularity')
    elif sort == 'rating':
        assortments = assortments.order_by(OrderBy(F('avg_rating'), descending=True, nulls_last=True))

    filtered_assortment_ids = assortments.values_list('id', flat=True)

    filtered_options = FilterOption.objects.filter(
        products__id__in=filtered_assortment_ids
    ).annotate(
        count_in_category=Count(
            'products',
            filter=Q(products__id__in=filtered_assortment_ids)
        )
    ).distinct()

    filter_groups = FilterGroup.objects.filter(
        options__in=filtered_options
    ).distinct().prefetch_related(
        Prefetch('options', queryset=filtered_options)
    )

    if request.user.is_authenticated:
        favorites_ids = list(request.user.favorites.values_list('product_id', flat=True))
    else:
        favorites_ids = []

    return render(request, 'assortment/assortment_list.html', {
        'assortments': assortments,
        'categories': categories,
        'selected_category': selected_category,
        'current_category': current_category,
        'filter_groups': filter_groups,
        'selected_filter_ids': selected_filter_ids,
        'query': query,
        'discounted_only': discounted_only,
        'new_only': new_only,
        'favorites_ids': favorites_ids,
    })



def assortment_detail(request, pk):
    assortment = get_object_or_404(Assortment, pk=pk)
    variants = assortment.variants.all()
    reviews = assortment.reviews.select_related('user')
    images = assortment.images.all()

    # Обновляем популярность товара раз в 24 часа
    viewed = request.session.get('viewed_products', {})
    last_viewed_str = viewed.get(str(pk))
    should_update = False

    try:
        if last_viewed_str:
            last_viewed = timezone.datetime.fromisoformat(last_viewed_str)
            if timezone.now() - last_viewed > timedelta(hours=24):
                should_update = True
        else:
            should_update = True
    except Exception:
        should_update = True

    if should_update:
        Assortment.objects.filter(pk=pk).update(popularity=F('popularity') + 1)
        viewed[str(pk)] = timezone.now().isoformat()
        request.session['viewed_products'] = viewed

    # Подготовка формы отзыва
    form = None
    user_review = None
    edit_mode = False
    edit_review = None

    if request.user.is_authenticated:
        user_review = Review.objects.filter(user=request.user, assortment=assortment).first()
        edit_id = request.GET.get('edit')

        # Редактирование отзыва
        if edit_id:
            edit_review = get_object_or_404(Review, id=edit_id, user=request.user, assortment=assortment)
            edit_mode = True

        if request.method == 'POST':
            if 'edit_review_id' in request.POST:
                # Обновление существующего отзыва
                edit_review = get_object_or_404(
                    Review, id=request.POST['edit_review_id'], user=request.user, assortment=assortment
                )
                form = ReviewForm(request.POST, instance=edit_review)
                if form.is_valid():
                    form.save()
                    messages.success(request, "Відгук оновлено!")
                    return redirect('assortment_detail', pk=pk)
                edit_mode = True
            elif not user_review:
                # Добавление нового отзыва
                form = ReviewForm(request.POST)
                if form.is_valid():
                    review = form.save(commit=False)
                    review.user = request.user
                    review.assortment = assortment
                    review.save()
                    messages.success(request, "Ваш відгук додано!")
                    return redirect('assortment_detail', pk=pk)
            else:
                form = ReviewForm(instance=edit_review) if edit_review else None
        else:
            form = ReviewForm(instance=edit_review) if edit_mode else (ReviewForm() if not user_review else None)

    context = {
        'assortment': assortment,
        'variants': variants,
        'reviews': reviews,
        'form': form,
        'user_review': user_review,
        'edit_mode': edit_mode,
        'edit_review': edit_review,
        'images': images,
    }

    return render(request, 'assortment/assortment_detail.html', context)

@login_required
def edit_review_view(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Відгук оновлено.')
            return redirect('assortment_detail', pk=review.assortment.pk)
    else:
        form = ReviewForm(instance=review)
    return render(request, 'reviews/edit_review.html', {'form': form, 'review': review})

@login_required
def delete_review_view(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    assortment_id = review.assortment.pk
    review.delete()
    messages.success(request, 'Відгук видалено.')
    return redirect('assortment_detail', pk=assortment_id)

# AJAX поиск
@require_GET
def search_suggest(request):
    q = request.GET.get('q', '').strip()
    results = []

    if q:
        matches = (
            Assortment.objects
            .filter(
                Q(assortment_name__icontains=q) |
                Q(assortment_description__icontains=q) |
                Q(tags__name__icontains=q) |
                Q(assortment_categories__category__icontains=q) |
                Q(filters__name__icontains=q) |
                Q(filters__group__name__icontains=q)
            )
            .prefetch_related('assortment_categories')
            .distinct()[:6]
        )

        for item in matches:
            first_category = item.assortment_categories.first()
            results.append({
                'name': item.assortment_name,
                'url': f"/assortment/{item.pk}/",
                'category': first_category.category if first_category else '',
            })

    return JsonResponse({'results': results})