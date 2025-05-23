from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.utils import timezone
import random
import string
from accounts.validators import validate_ukrainian_phone


# Кастомный менеджер для модели пользователя
class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    # Создание обычного пользователя
    def create_user(self, email, password=None, phone=None, **extra_fields):
        if not email:
            raise ValueError('Email обовʼязковий')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    # Создание суперпользователя
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Суперюзер має мати is_staff=True')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Суперюзер має мати is_superuser=True')

        return self.create_user(email, password, **extra_fields)

# Кастомная модель пользователя
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, unique=True, null=True, validators=[validate_ukrainian_phone])
    is_verified = models.BooleanField(default=False)

    # Убираем стандартное поле username
    username = None
    USERNAME_FIELD = 'email' # Авторизация по email
    REQUIRED_FIELDS = []

    objects = CustomUserManager() # Подключаем кастомный менеджер

# Модель для хранения кодов подтверждения
class VerificationCode(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    last_sent_at = models.DateTimeField()

    # Проверка, истёк ли срок действия кода
    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=15)

    def can_resend(self):
        return timezone.now() - self.last_sent_at >= timezone.timedelta(seconds=60)

    # Генерация случайного 6-значного кода
    @staticmethod
    def generate_code():
        return ''.join(random.choices(string.digits, k=6))
