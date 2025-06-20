from django.shortcuts import render, get_object_or_404, redirect
from django.db.models.expressions import OrderBy
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_GET
from django.db.models import Q, Prefetch, Count, Case, When, F, Subquery, OuterRef, DecimalField, Avg
from django.contrib.auth.decorators import login_required
from .models import (
    Assortment, Category,
    AssortmentVariant, FilterGroup, FilterOption, Review
)
from producer.models import Producer
from .forms import ReviewForm
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict
from django.core.paginator import Paginator
from django.urls import reverse

def category_list_view(request):
    categories = Category.objects.all().order_by('created_at')
    return render(request, 'assortment/category_list.html', {'categories': categories})

def chunked(iterable, size):
    for i in range(0, len(iterable), size):
        yield iterable[i:i + size]


def assortment_list(request, slug=None, producer_slug=None):
    # 1. Базовые параметры
    all_categories = Category.objects.all().order_by('created_at')
    selected_category = slug or request.GET.get('category')
    selected_filter_ids = list(map(int, request.GET.getlist('filters')))  # список выбранных option.id
    selected_producer_slugs = request.GET.getlist('producer')
    selected_producers = []
    if selected_producer_slugs:
        selected_producers = list(Producer.objects.filter(slug__in=selected_producer_slugs))
    query = request.GET.get('q', '')
    sort = request.GET.get('sort')
    new_only = request.GET.get('new') == '1'
    my_favorites_only = request.GET.get('my_favorites') == '1'
    page = request.GET.get('page', 1)

    # 2. Базовая выборка (до фильтров)
    base_assortments = Assortment.objects.all()

    # Handle producer filtering by slug
    current_producer = None
    if producer_slug:
        current_producer = get_object_or_404(Producer, slug=producer_slug)
        base_assortments = base_assortments.filter(producer=current_producer)
    elif selected_producer_slugs:
        base_assortments = base_assortments.filter(producer__slug__in=selected_producer_slugs)

    current_category = None
    if selected_category:
        try:
            current_category = Category.objects.get(slug=selected_category)
            base_assortments = base_assortments.filter(
                assortment_categories=current_category
            )
        except Category.DoesNotExist:
            pass

    if query:
        base_assortments = base_assortments.filter(
            Q(assortment_name__icontains=query) |
            Q(assortment_description__icontains=query) |
            Q(assortment_categories__category__icontains=query) |
            Q(tags__name__icontains=query) |
            Q(filters__name__icontains=query) |
            Q(filters__group__name__icontains=query)
        ).distinct()

    if new_only:
        base_assortments = base_assortments.filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=30)
        )

    if my_favorites_only and request.user.is_authenticated:
        from favorites.models import Favorite
        favorite_ids = Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)
        base_assortments = base_assortments.filter(id__in=favorite_ids)

    # 3. Фильтруем по производителям (но еще не по фильтрам)
    assortment_for_facet = base_assortments
    if selected_producer_slugs:
        assortment_for_facet = assortment_for_facet.filter(producer__slug__in=selected_producer_slugs)

    # 4. Применяем выбранные фильтры к товарам (итоговый список) с учётом группировки
    assortments = assortment_for_facet

    if selected_filter_ids:
        # Сначала сгруппируем выбранные filter_id по group_id
        all_options = FilterOption.objects.select_related('group').all()
        option_group_map = {opt.id: opt.group_id for opt in all_options}

        group_to_option_ids = defaultdict(list)
        for opt_id in selected_filter_ids:
            grp_id = option_group_map.get(opt_id)
            if grp_id is not None:
                group_to_option_ids[grp_id].append(opt_id)

        # Теперь для каждой группы из выбранных делаем фильтрацию "filters__id__in [...]"
        for grp_id, opts_list in group_to_option_ids.items():
            # ИЛИ внутри этой группы
            assortments = assortments.filter(filters__id__in=opts_list)

    # После этого данные для итогу:
    filtered_assortment_ids = list(assortments.values_list('id', flat=True))

    # 5. Производители для сайдбара (до применения фильтров)
    # Get all producers that have products in the current category or all products if no category
    if current_category:
        sidebar_producers = Producer.objects.filter(
            assortment__assortment_categories=current_category
        ).distinct().annotate(
            product_count=Count('assortment', filter=Q(assortment__assortment_categories=current_category))
        ).order_by('producer_name')
    else:
        sidebar_producers = Producer.objects.filter(
            assortment__isnull=False
        ).distinct().annotate(
            product_count=Count('assortment')
        ).order_by('producer_name')

    # === 6. Считаем фасетные счетчики для всех опций ===
    all_filter_groups = FilterGroup.objects.prefetch_related('options')
    # all_options мы уже получили выше, но можно ещё раз:
    all_options = FilterOption.objects.select_related('group').all()

    # Сгруппируем реальные выбранные фильтры по группам:
    group_selected_options = defaultdict(list)
    for opt_id in selected_filter_ids:
        grp_id = option_group_map.get(opt_id)
        if grp_id:
            group_selected_options[grp_id].append(opt_id)

    option_counts_dict = {}

    for option in all_options:
        current_group_id = option.group_id

        # Начинаем с полного набора ассортиментов без фильтров (от объектов без фильтров мы уже сохранили в assortment_for_facet)
        qs_for_count = assortment_for_facet

        # Для каждой группы строим условие:
        for grp in all_filter_groups:
            if grp.id == current_group_id:
                # внутри «своей» группы подставляем только эту единственную опцию
                opts_in_this_grp = [option.id]
            else:
                # для остальных групп берём реальные выбранные пользователем (если они есть)
                opts_in_this_grp = group_selected_options.get(grp.id, [])

            if opts_in_this_grp:
                qs_for_count = qs_for_count.filter(filters__id__in=opts_in_this_grp)

        count = qs_for_count.distinct().count()
        option_counts_dict[option.id] = count

    # 7. Считаем общее число товаров для каждого фильтра (без учёта выбранных фильтров):
    option_counts_total = (
        FilterOption.objects
        .annotate(total_count=Count('products'))
    )
    option_total_dict = {o.id: o.total_count for o in option_counts_total}

    # 8. Считаем цены и рейтинг для ассортиментов
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

    # 9. Сортировка
    if sort == 'price_asc':
        assortments = assortments.order_by('effective_price')
    elif sort == 'price_desc':
        assortments = assortments.order_by('-effective_price')
    elif sort == 'newest':
        assortments = assortments.order_by('-created_at')
    elif sort == 'popular':
        assortments = assortments.order_by('-popularity')
    elif sort == 'rating':
        assortments = assortments.order_by(Avg('reviews__rating').desc(nulls_last=True))

    # 10. Избранные товары пользователя
    if request.user.is_authenticated:
        favorites_ids = list(request.user.favorites.values_list('product_id', flat=True))
    else:
        favorites_ids = []

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'assortment/partials/product_grid.html', {
            'assortments': assortments,
            'favorites_ids': favorites_ids,
        })

    # Add pagination
    paginator = Paginator(assortments, 12)  # Show 24 items per page
    try:
        assortments = paginator.page(page)
    except:
        assortments = paginator.page(1)

    total_products = Assortment.objects.count()

    return render(request, 'assortment/assortment_list.html', {
        'assortments': assortments,
        'selected_category': selected_category,
        'current_category': current_category,
        'current_producer': current_producer,
        'total_products': total_products,
        'filter_groups': all_filter_groups,
        'option_counts': option_counts_dict,     # фасетные счётчики (после правки)
        'option_total_dict': option_total_dict,
        'selected_filter_ids': selected_filter_ids,
        'selected_producers': selected_producers,
        'active_producers': sidebar_producers,
        'selected_producer_ids': selected_producer_slugs,
        'query': query,
        'sort': sort,
        'new_only': new_only,
        'my_favorites_only': my_favorites_only,
        'favorites_ids': favorites_ids,
        'categories': all_categories,
    })



def assortment_detail(request, slug):
    assortment = get_object_or_404(Assortment, slug=slug)
    variants = assortment.variants.all()
    reviews = assortment.reviews.select_related('user')
    images = assortment.images.all()

    # Обновляем популярность товара раз в 24 часа
    viewed = request.session.get('viewed_products', {})
    last_viewed_str = viewed.get(str(assortment.id))
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
        Assortment.objects.filter(pk=assortment.id).update(popularity=F('popularity') + 1)
        viewed[str(assortment.id)] = timezone.now().isoformat()
        request.session['viewed_products'] = viewed

    # Форма для отзыва
    form = None
    user_review = None

    if request.user.is_authenticated:
        user_review = Review.objects.filter(user=request.user, assortment=assortment).first()
        if request.method == 'POST' and not user_review:
            # Добавление нового отзыва
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.assortment = assortment
                review.save()
                messages.success(request, "Ваш відгук додано!")
                return redirect('assortment_detail', slug=slug)
        else:
            form = ReviewForm() if not user_review else None

    # Получаем список избранных товаров
    if request.user.is_authenticated:
        favorites_ids = list(request.user.favorites.values_list('product_id', flat=True))
    else:
        favorites_ids = []

    context = {
        'assortment': assortment,
        'variants': variants,
        'reviews': reviews,
        'form': form,
        'user_review': user_review,
        'images': images,
        'favorites_ids': favorites_ids,
    }

    return render(request, 'assortment/assortment_detail.html', context)

@login_required
def delete_review_view(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if review.user != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("Ви не маєте права видаляти цей відгук.")
    assortment_slug = review.assortment.slug
    review.delete()
    messages.success(request, 'Відгук видалено.')
    return redirect('assortment_detail', slug=assortment_slug)

# AJAX поиск
@require_GET
def search_suggest(request):
    q = request.GET.get('q', '').strip()
    results = []

    if q:
        # First try exact matches
        exact_matches = (
            Assortment.objects
            .filter(
                Q(assortment_name__iexact=q) |
                Q(assortment_categories__category__iexact=q)
            )
            .prefetch_related('assortment_categories')
            .distinct()[:3]
        )

        # Then try partial matches
        partial_matches = (
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
            .exclude(id__in=exact_matches.values_list('id', flat=True))
            .distinct()[:3]
        )

        # Process exact matches first
        for item in exact_matches:
            categories = [cat.category for cat in item.assortment_categories.all()]
            image_url = item.poster.url if item.poster else ''
            results.append({
                'name': item.assortment_name,
                'url': reverse('assortment_detail', kwargs={'slug': item.slug}),
                'categories': categories,
                'image': image_url,
                'type': 'exact_match',
                'price': str(item.price) if item.price else '',
            })

        # Then process partial matches
        for item in partial_matches:
            categories = [cat.category for cat in item.assortment_categories.all()]
            image_url = item.poster.url if item.poster else ''
            results.append({
                'name': item.assortment_name,
                'url': reverse('assortment_detail', kwargs={'slug': item.slug}),
                'categories': categories,
                'image': image_url,
                'type': 'partial_match',
                'price': str(item.price) if item.price else '',
            })

        # Add category suggestions if we have less than 6 results
        if len(results) < 6:
            # Get all categories that match the search query
            category_matches = (
                Category.objects
                .filter(category__icontains=q)
                .distinct()[:6 - len(results)]
            )
            
            for category in category_matches:
                results.append({
                    'name': category.category,
                    'url': reverse('category_detail', kwargs={'slug': category.slug}),
                    'type': 'category',
                    'image': '',
                })

    return JsonResponse({'results': results})