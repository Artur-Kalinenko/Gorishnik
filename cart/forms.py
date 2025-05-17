from django import forms

class OrderForm(forms.Form):
    full_name = forms.CharField(label='ПІБ', max_length=255)
    phone = forms.CharField(label='Телефон', max_length=20)
    email = forms.EmailField(label='Email')
    delivery_method = forms.ChoiceField(
        label='Спосіб доставки',
        choices=[
            ('nova_poshta', 'Нова Пошта'),
            ('ukr_poshta', 'Укрпошта'),
            ('pickup', 'Самовивіз'),
        ],
        widget=forms.Select(attrs={'id': 'delivery-method'})
    )
    address = forms.CharField(
        label='Адреса відділення',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'id': 'address-field'})
    )
