from django import forms

# Форма оформления заказа без регистрации
class OrderForm(forms.Form):
    full_name = forms.CharField(label='ПІБ', max_length=255)
    phone = forms.CharField(label='Телефон', max_length=20)
    email = forms.EmailField(label='Email')

    # Выбор способа доставки
    delivery_method = forms.ChoiceField(
        label='Спосіб доставки',
        choices=[
            ('nova_poshta', 'Нова Пошта'),
            ('ukr_poshta', 'Укрпошта'),
            ('pickup', 'Самовивіз'),
        ],
        widget=forms.Select(attrs={'id': 'delivery-method'})
    )
    # Адрес отделения (только если выбран не самовывоз)
    address = forms.CharField(
        label='Адреса відділення',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'id': 'address-field'})
    )
