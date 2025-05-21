from django import forms
from django.contrib.auth.forms import SetPasswordForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from .models import CustomUser

# --- Валидатор пароля ---
def validate_custom_password(password):
    errors = []
    if len(password) < 8:
        errors.append("Пароль повинен містити щонайменше 8 символів.")
    if password.isdigit():
        errors.append("Пароль не може складатися лише з цифр.")
    common_passwords = ['123456', 'password', 'qwerty', '111111']
    if password.lower() in common_passwords:
        errors.append("Пароль надто відомий.")
    if errors:
        raise ValidationError(errors)

# --- Регистрация и вход ---
class RegistrationForm(forms.Form):
    first_name = forms.CharField(label="Ім'я", required=True)
    email = forms.EmailField(label='Email', required=True)
    phone = forms.CharField(label='Телефон', required=False)
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Підтвердіть пароль', widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data['email']
        user = CustomUser.objects.filter(email=email).first()
        if user and user.is_verified:
            raise forms.ValidationError("Користувач з таким email вже існує.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            user = CustomUser.objects.filter(phone=phone).first()
            if user and user.is_verified:
                raise forms.ValidationError("Користувач з таким телефоном вже існує.")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Паролі не співпадають.")
            try:
                validate_custom_password(password1)
            except ValidationError as e:
                self.add_error('password1', e)
        return cleaned_data

class LoginForm(forms.Form):
    identifier = forms.CharField(label='Email або телефон')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

# --- Сброс пароля ---
class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Ваша електронна адреса")

    def clean_email(self):
        email = self.cleaned_data['email']
        if not CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Користувача з таким email не існує.')
        return email

class PasswordResetCodeForm(forms.Form):
    code = forms.CharField(label="Код підтвердження")

class SetNewPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label='Новий пароль', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='Підтвердіть новий пароль', widget=forms.PasswordInput)

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
    new_email = forms.EmailField(label='Новий email')

    def clean_new_email(self):
        email = self.cleaned_data['new_email']
        if CustomUser.objects.filter(email=email, is_verified=True).exists():
            raise forms.ValidationError("Користувач з таким email вже існує.")
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
            'first_name': "Ім’я",
            'phone': "Телефон",
        }
