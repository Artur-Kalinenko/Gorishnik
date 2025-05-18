from django import template

# Регистрируем библиотеку шаблонных тегов
register = template.Library()

# Фильтр для добавления CSS-класса к полю формы
@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})