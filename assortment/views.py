from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Prefetch, Count
from .models import (
    Assortment, Category,
    AssortmentVariant, FilterGroup, FilterOption
)


def assortment_list(request):
    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    selected_filter_ids = list(map(int, request.GET.getlist('filters')))
    query = request.GET.get('q', '')

    assortments = Assortment.objects.prefetch_related('variants').all()
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
            Q(assortment_categories__category__icontains=query)
        )

    # Получаем ID всех товаров после фильтрации
    filtered_assortment_ids = assortments.values_list('id', flat=True)

    # Опции фильтров, которые действительно используются в отфильтрованных товарах
    filtered_options = FilterOption.objects.filter(
        products__id__in=filtered_assortment_ids
    ).annotate(
        count_in_category=Count(
            'products',
            filter=Q(products__id__in=filtered_assortment_ids)
        )
    ).distinct()

    # Группы фильтров, содержащие только активные опции
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
    return render(request, 'assortment/assortment_detail.html', {
        'assortment': assortment,
        'variants': variants,
    })
