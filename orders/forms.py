from django import forms
from accounts.validators import validate_ukrainian_phone

class OrderForm(forms.Form):
    full_name = forms.CharField(label='ПІБ', max_length=255)
    phone = forms.CharField(
        label='Телефон',
        max_length=20,
        widget=forms.TextInput(attrs={'id': 'order-phone-input'}),
        validators=[validate_ukrainian_phone]
    )
    email = forms.EmailField(label='Email')

    delivery_method = forms.ChoiceField(
        label='Спосіб доставки',
        choices=[
            ('nova_poshta', 'Нова Пошта'),
            ('ukr_poshta', 'Укрпошта'),
            ('pickup', 'Самовивіз'),
        ],
        widget=forms.RadioSelect
    )
