from django import forms
from accounts.validators import validate_ukrainian_phone
from django.utils.translation import gettext_lazy as _

class OrderForm(forms.Form):
    full_name = forms.CharField(
        label=_('Full name'),
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Recipient full name')})
    )
    phone = forms.CharField(
        label=_('Phone'),
        max_length=20,
        widget=forms.TextInput(attrs={'id': 'order-phone-input', 'class': 'form-control', 'placeholder': _('Recipient contact number')}),
        validators=[validate_ukrainian_phone]
    )
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Your email address')})
    )

    delivery_method = forms.ChoiceField(
        label=_('Delivery method'),
        choices=[
            ('nova_poshta', _('Nova Poshta')),
            ('ukr_poshta', _('Ukrposhta')),
            ('pickup', _('Self-pickup')),
        ],
        widget=forms.RadioSelect
    )

    additional_notes = forms.CharField(
        label=_('Additional notes'),
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('Your order preferences. If you are ordering delivery as a gift, please provide your phone number and name for contact!')})
    )

    PAYMENT_CHOICES = [
        ('cod', _('Cash on delivery')),
        ('online', _('Online payment')),
        ('invoice', _('Payment by invoice')),
    ]
    payment_method = forms.ChoiceField(
        label=_('Payment method'),
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect,
        initial='cod'
    )

