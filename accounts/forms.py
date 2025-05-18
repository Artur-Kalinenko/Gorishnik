from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import ValidationError
from .models import CustomUser

# Валидация пароля: длина, только цифры, слишком простые пароли
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

# Форма регистрации пользователя
class RegistrationForm(forms.Form):
    first_name = forms.CharField(label="Ім'я", required=True)
    email = forms.EmailField(label='Email', required=True)
    phone = forms.CharField(label='Телефон', required=False)
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Підтвердіть пароль', widget=forms.PasswordInput)

    # Проверка уникальности email (если уже есть подтверждённый пользователь)
    def clean_email(self):
        email = self.cleaned_data['email']
        user = CustomUser.objects.filter(email=email).first()
        if user and user.is_verified:
            raise forms.ValidationError("Користувач з таким email вже існує.")
        return email

    # Проверка уникальности телефона (если уже есть подтверждённый пользователь)
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            user = CustomUser.objects.filter(phone=phone).first()
            if user and user.is_verified:
                raise forms.ValidationError("Користувач з таким телефоном вже існує.")
        return phone

    # Общая проверка: совпадают ли пароли и проходят ли проверку сложности
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

# Форма входа (по email или телефону)
class LoginForm(forms.Form):
    identifier = forms.CharField(label='Email або телефон')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

# Запрос на сброс пароля
class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Ваша електронна адреса")

# Ввод кода подтверждения при сбросе пароля
class PasswordResetCodeForm(forms.Form):
    code = forms.CharField(label="Код підтвердження")

# Установка нового пароля
class SetNewPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label='Новий пароль', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='Підтвердіть новий пароль', widget=forms.PasswordInput)

    # Проверка сложности нового пароля
    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if password:
            try:
                validate_custom_password(password)
            except ValidationError as e:
                raise forms.ValidationError(e)
        return password
