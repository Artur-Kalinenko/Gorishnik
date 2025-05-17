from django.shortcuts import render
from .models import Producer

def producer_list(request):
    producers = Producer.objects.all()
    return render(request, 'producers/producers_list.html', {'producers': producers})
