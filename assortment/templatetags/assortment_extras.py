from django import template

register = template.Library()

@register.filter
def pluralize_products_ukr(count):
    count = int(count)
    if count == 1:
        return "продукт"
    elif 2 <= count % 10 <= 4 and (count < 10 or count > 20):
        return "продукти"
    else:
        return "продуктів"
