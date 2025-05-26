from .models import Category
from .views import chunked

def categories_processor(request):
    return {
        'categories': Category.objects.all()
    }

def categories_columns(request):
    all_categories = Category.objects.all().order_by('created_at')
    columns = list(chunked(all_categories, 10))
    return {'categories_columns': columns}