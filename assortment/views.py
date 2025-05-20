from django.shortcuts import render, get_object_or_404
from django.db.models.functions import Coalesce
from django.db.models.expressions import OrderBy
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import Q, Prefetch, Count, Min, Max, Case, When, F, Value, Subquery, OuterRef, DecimalField, Avg
from .models import (
    Assortment, Category,
    AssortmentVariant, FilterGroup, FilterOption, Review
)
from .forms import ReviewForm
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta


def assortment_list(request):
    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    selected_filter_ids = list(map(int, request.GET.getlist('filters')))
    query = request.GET.get('q', '')
    sort = request.GET.get('sort')

    assortments = Assortment.objects.all()
    current_category = None

    # Фильтрация по категории
    if selected_category:
        assortments = assortments.filter(assortment_categories__category=selected_category)
        current_category = categories.filter(category=selected_category).first()

    # Фильтрация по фильтрам
    if selected_filter_ids:
        for filter_id in selected_filter_ids:
            assortments = assortments.filter(filters__id=filter_id)

    # Поиск
    if query:
        assortments = assortments.filter(
            Q(assortment_name__icontains=query) |
            Q(assortment_description__icontains=query) |
            Q(assortment_categories__category__icontains=query) |
            Q(tags__name__icontains=query) |
            Q(filters__name__icontains=query) |
            Q(filters__group__name__icontains=query)
        ).distinct()

    # 🔍 Subquery для min и max цен по вариантам
    variant_qs = AssortmentVariant.objects.filter(assortment=OuterRef('pk'))

    if sort == 'price_desc':
        price_subquery = Subquery(variant_qs.order_by('-price').values('price')[:1])
    else:  # по умолчанию и для price_asc, popular, newest
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

    # Сортировка
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

    # ID всех отфильтрованных товаров
    filtered_assortment_ids = assortments.values_list('id', flat=True)

    # Опции фильтров
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

    return render(request, 'assortment/assortment_list.html', {
        'assortments': assortments,
        'categories': categories,
        'selected_category': selected_category,
        'current_category': current_category,
        'filter_groups': filter_groups,
        'selected_filter_ids': selected_filter_ids,
        'query': query,
    })



def assortment_detail(request, pk):
    assortment = get_object_or_404(Assortment, pk=pk)
    variants = assortment.variants.all()
    reviews = assortment.reviews.select_related('user')

    # Увеличиваем popular только раз в 24 часа
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

    # Отзыв
    form = None
    user_review = None

    if request.user.is_authenticated:
        user_review = Review.objects.filter(user=request.user, assortment=assortment).first()
        if not user_review:
            if request.method == 'POST':
                form = ReviewForm(request.POST)
                if form.is_valid():
                    review = form.save(commit=False)
                    review.user = request.user
                    review.assortment = assortment
                    review.save()
                    messages.success(request, "Ваш відгук додано!")
                    return redirect('assortment_detail', pk=pk)
            else:
                form = ReviewForm()

    return render(request, 'assortment/assortment_detail.html', {
        'assortment': assortment,
        'variants': variants,
        'reviews': reviews,
        'form': form,
        'user_review': user_review,
    })

# AJAX поиск
@require_GET
def search_suggest(request):
    q = request.GET.get('q', '').strip()
    results = []

    if q:
        matches = Assortment.objects.filter(
            Q(assortment_name__icontains=q) |
            Q(assortment_description__icontains=q) |
            Q(tags__name__icontains=q) |
            Q(assortment_categories__category__icontains=q) |
            Q(filters__name__icontains=q) |
            Q(filters__group__name__icontains=q)
        ).distinct()[:6]

        for item in matches:
            results.append({
                'name': item.assortment_name,
                'url': f"/assortment/{item.pk}/",
                'category': item.assortment_categories.category if item.assortment_categories else '',
            })

    return JsonResponse({'results': results})