from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Assortment, Category, AssortmentVariant

def assortment_list(request):
    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    query = request.GET.get('q', '')

    assortments = Assortment.objects.prefetch_related('variants').all()
    current_category = None

    if selected_category:
        assortments = assortments.filter(assortment_categories__category=selected_category)
        current_category = categories.filter(category=selected_category).first()

    if query:
        assortments = assortments.filter(
            Q(assortment_name__icontains=query) |
            Q(assortment_categories__category__icontains=query)
        )

    return render(request, 'assortment/assortment_list.html', {
        'assortments': assortments,
        'categories': categories,
        'selected_category': selected_category,
        'current_category': current_category,
        'query': query,
    })

def assortment_detail(request, pk):
    assortment = get_object_or_404(Assortment, pk=pk)
    variants = assortment.variants.all()
    return render(request, 'assortment/assortment_detail.html', {
        'assortment': assortment,
        'variants': variants,
    })

def welcome(request):
    return render(request, 'pages/welcome.html')

def reviews(request):
    return render(request, 'pages/reviews.html')

def delivery(request):
    return render(request, 'pages/delivery.html')
