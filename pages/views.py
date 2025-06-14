from django.shortcuts import render
from django.http import HttpResponse

# Главная страница
def welcome(request):
    return render(request, 'pages/welcome.html')

# Страница отзывов
def reviews(request):
    return render(request, 'pages/reviews.html')

# Страница доставки
def delivery(request):
    return render(request, 'pages/delivery.html')

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /cart/",
        "Disallow: /accounts/",
        "Disallow: /static/",
        "Disallow: /media/",
        "Disallow: /payments/",
        "Disallow: /orders/",
        "Allow: /media/assortment/",
        "Allow: /static/",
        "Sitemap: https://gorishnik.ua/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")