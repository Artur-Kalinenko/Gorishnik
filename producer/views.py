from django.shortcuts import render
from .models import Producer


# Представление для отображения списка всех производителей
def producer_list(request):
    producers = Producer.objects.all()
    return render(request, 'producer/producers_list.html', {'producers': producers})
