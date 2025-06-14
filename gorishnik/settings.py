from pathlib import Path
from decouple import config
from django.utils.translation import gettext_lazy as _
import os

BASE_DIR = Path(__file__).resolve().parent.parent

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

SECRET_KEY = config('DJANGO_SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = ['0.0.0.0', 'localhost', '127.0.0.1', '.ngrok-free.app',]

CSRF_TRUSTED_ORIGINS = [
    "https://*.ngrok-free.app",
]


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_cleanup.apps.CleanupConfig',
    'social_django',
    'django_crontab',
    'modeltranslation',
    'django.contrib.sitemaps',
    #my_apps
    'assortment.apps.AssortmentConfig',
    'producer',
    'cart',
    'accounts',
    'pages',
    'orders',
    'payments',
    'delivery',
    'favorites',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gorishnik.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.views.base_context', # Контекст корзины доступен во всех шаблонах
                'assortment.context_processors.categories_processor',
                'assortment.context_processors.categories_columns',
            ],
        },
    },
]

WSGI_APPLICATION = 'gorishnik.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}

# отключены, используется своя валидация
AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]

AUTH_USER_MODEL = 'accounts.CustomUser'


LANGUAGES = [
    ('uk', _('Українська')),
    ('ru', _('Русский')),
]

LANGUAGE_CODE = 'uk'

TIME_ZONE = 'Europe/Kyiv'

USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

AUTHENTICATION_BACKENDS = [
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'welcome'
LOGOUT_REDIRECT_URL = 'welcome'


SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = config('GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = config('GOOGLE_OAUTH2_SECRET')

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'accounts.pipeline.set_verified',
    'accounts.pipeline.transfer_guest_cart',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

SOCIAL_AUTH_LOGIN_ERROR_URL = '/login/?cancel=1'


LIQPAY_PUBLIC_KEY = config('LIQPAY_PUBLIC_KEY')
LIQPAY_PRIVATE_KEY = config('LIQPAY_PRIVATE_KEY')
LIQPAY_SANDBOX = config('LIQPAY_SANDBOX', cast=bool)

NOVA_POSHTA_API_KEY = os.getenv('NOVA_POSHTA_API_KEY')

CRONJOBS = [
    ('0 2 * * *', 'django.core.management.call_command', ['backup_db']),
    ('0 3 * * *', 'django.core.management.call_command', ['clear_cart']),
    ('0 4 * * *', 'django.core.management.call_command', ['clear_verification_codes']),
    ('0 5 * * *', 'django.core.management.call_command', ['delete_unverified_users']),
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

# Добавляем настройки для языка
LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_AGE = 365 * 24 * 60 * 60  # 1 год
LANGUAGE_COOKIE_DOMAIN = None
LANGUAGE_COOKIE_PATH = '/'
LANGUAGE_COOKIE_SECURE = False
LANGUAGE_COOKIE_HTTPONLY = False
LANGUAGE_COOKIE_SAMESITE = None
