import re
from django.core.exceptions import ValidationError

#валидатор номера телефона
def validate_ukrainian_phone(value):
    pattern = r'^\+380 \(\d{2}\) \d{3}-\d{2}-\d{2}$'
    if not re.match(pattern, value):
        raise ValidationError('Невірний формат номера. Використовуйте +380 (XX) XXX-XX-XX')

#валидатор пароля
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