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
    save_pre_social_session,
    change_email_request_view,
    confirm_change_email_view,
    change_password_view,
    confirm_change_password_view,
)
from social_django.urls import urlpatterns as social_urls

urlpatterns = [
    # --- Регистрация и верификация ---
    path('register/', register_view, name='register'),
    path('verify-email/', verify_email_view, name='verify_email'),

    # --- Аутентификация ---
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # --- Авторизация через Google ---
    path('auth/complete/<str:backend>/', google_login_complete_safe, name='google_complete'),
    path('auth/', include('social_django.urls', namespace='social')),

    # --- Сброс пароля ---
    path('password-reset/', password_reset_request_view, name='password_reset_request'),
    path('password-reset/verify/', password_reset_code_view, name='password_reset_code'),
    path('password-reset/set-new/', password_reset_new_password_view, name='set_new_password'),

    # --- Смена email и пароля через кабинет юзера---
    path('cabinet/change-email/', change_email_request_view, name='change_email'),
    path('cabinet/confirm-email/', confirm_change_email_view, name='confirm_change_email'),
    path('cabinet/change-password/', change_password_view, name='change_password'),
    path('cabinet/confirm-password/', confirm_change_password_view, name='confirm_change_password'),

    # --- Кабинет пользователя ---
    path('cabinet/', user_cabinet_view, name='user_cabinet'),
    path('cabinet/edit/', edit_profile_view, name='edit_profile'),

    # --- Служебное ---
    path('save-pre-session/', save_pre_social_session, name='save_pre_social_session'),
]