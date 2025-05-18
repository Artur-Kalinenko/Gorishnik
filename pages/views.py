from django.shortcuts import render

# Главная страница
def welcome(request):
    return render(request, 'pages/welcome.html')

# Страница отзывов
def reviews(request):
    return render(request, 'pages/reviews.html')

# Страница доставки
def delivery(request):
    return render(request, 'pages/delivery.html')
