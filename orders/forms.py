from django import forms
from accounts.validators import validate_ukrainian_phone

class OrderForm(forms.Form):
    full_name = forms.CharField(
        label='ПІБ',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ПІБ Отримувача'})
    )
    phone = forms.CharField(
        label='Телефон',
        max_length=20,
        widget=forms.TextInput(attrs={'id': 'order-phone-input', 'class': 'form-control', 'placeholder': 'Контактний номер отримувача'}),
        validators=[validate_ukrainian_phone]
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Адреса вашої електронної пошти'})
    )

    delivery_method = forms.ChoiceField(
        label='Спосіб доставки',
        choices=[
            ('nova_poshta', 'Нова Пошта'),
            ('ukr_poshta', 'Укрпошта'),
            ('pickup', 'Самовивіз'),
        ],
        widget=forms.RadioSelect
    )

    additional_notes = forms.CharField(
        label='Додаткові побажання',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ваші побажання до замовлення. Якщо ви замовляєте доставку у якості подарунка, будь ласка, вкажіть ваш номер телефону та імʼя для звʼязку з вами!'})
    )

    PAYMENT_CHOICES = [
        ('cod', 'Оплата при отриманні'),
        ('online', 'Оплата на сайті'),
        ('invoice', 'Оплата за реквізитами'),
    ]
    payment_method = forms.ChoiceField(
        label='Спосіб оплати',
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect,
        initial='cod'
    )

