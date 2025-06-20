from django import forms
from django.contrib.auth.forms import SetPasswordForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import CustomUser
from accounts.validators import validate_ukrainian_phone, validate_custom_password

# --- Регистрация и вход ---
class RegistrationForm(forms.Form):
    first_name = forms.CharField(label=_("Ім'я"), required=True)
    email = forms.EmailField(label=_('Email'), required=True)
    phone = forms.CharField(
        label=_('Телефон'),
        required=False,
        widget=forms.TextInput(attrs={
            'id': 'phone-input',
        })
    )
    password1 = forms.CharField(label=_('Пароль'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Підтвердіть пароль'), widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data['email']
        user = CustomUser.objects.filter(email=email).first()
        if user and user.is_verified:
            raise forms.ValidationError(_("Користувач з таким email вже існує."))
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            validate_ukrainian_phone(phone)
            user = CustomUser.objects.filter(phone=phone).first()
            if user and user.is_verified:
                raise forms.ValidationError(_("Користувач з таким телефоном вже існує."))
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_("Паролі не співпадають."))
            try:
                validate_custom_password(password1)
            except ValidationError as e:
                self.add_error('password1', e)
        return cleaned_data

class LoginForm(forms.Form):
    identifier = forms.CharField(
        label=_('Email або телефон'),
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('Введіть email або телефон')
            }
        )
    )
    password = forms.CharField(
        label=_('Пароль'),
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('Введіть пароль')
            }
        )
    )

# --- Сброс пароля ---
class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label=_("Ваша електронна адреса"))

    def clean_email(self):
        email = self.cleaned_data['email']
        if not CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Користувача з таким email не існує.'))
        return email

class PasswordResetCodeForm(forms.Form):
    code = forms.CharField(label=_("Код підтвердження"))

class SetNewPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label=_('Новий пароль'), widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=_('Підтвердіть новий пароль'), widget=forms.PasswordInput)

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if password:
            try:
                validate_custom_password(password)
            except ValidationError as e:
                raise forms.ValidationError(e)
        return password

# --- Смена email и пароля ---
class ChangeEmailForm(forms.Form):
    new_email = forms.EmailField(label=_('Новий email'))

    def clean_new_email(self):
        email = self.cleaned_data['new_email']
        if CustomUser.objects.filter(email=email, is_verified=True).exists():
            raise forms.ValidationError(_("Користувач з таким email вже існує."))
        return email

class CustomPasswordChangeForm(PasswordChangeForm):
    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        validate_custom_password(password)
        return password

# --- Редактирование профиля ---
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'phone']
        labels = {
            'first_name': _("Ім'я"),
            'phone': _("Телефон"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].widget.attrs.update({
            'id': 'edit-phone-input'
        })