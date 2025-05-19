from django.urls import path, include
from .views import (
    register_view, login_view, logout_view,
    verify_email_view,
    password_reset_request_view,
    password_reset_code_view,
    password_reset_new_password_view,
    user_cabinet_view,
    edit_profile_view,
    google_login_complete_safe,
    save_pre_social_session
)
from social_django.urls import urlpatterns as social_urls

urlpatterns = [
    # Регистрация и верификация
    path('register/', register_view, name='register'),
    path('verify-email/', verify_email_view, name='verify_email'),

    # Логин и логаут
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Авторизация через Google
    path('auth/complete/<str:backend>/', google_login_complete_safe, name='google_complete'),
    path('auth/', include('social_django.urls', namespace='social')),

    # Сброс пароля
    path('password-reset/', password_reset_request_view, name='password_reset_request'),
    path('password-reset/verify/', password_reset_code_view, name='password_reset_code'),
    path('password-reset/set-new/', password_reset_new_password_view, name='set_new_password'),

    # Кабинет пользователя
    path('cabinet/', user_cabinet_view, name='user_cabinet'),
    path('cabinet/edit/', edit_profile_view, name='edit_profile'),

    # Сохранение сессии
    path('save-pre-session/', save_pre_social_session, name='save_pre_social_session'),
]