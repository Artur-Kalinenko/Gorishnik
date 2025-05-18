from django.shortcuts import render, redirect
from .forms import (
    RegistrationForm,
    LoginForm,
    PasswordResetRequestForm,
    PasswordResetCodeForm,
    SetNewPasswordForm
)
from .models import CustomUser, VerificationCode
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.db import IntegrityError
from datetime import timedelta
from django.utils import timezone
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
from cart.models import Order, Cart
from social_core.exceptions import AuthCanceled
from social_django.views import complete


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            password = form.cleaned_data['password1']

            # Удаляем старый неверифицированный аккаунт с таким email
            existing_email_user = CustomUser.objects.filter(email=email).first()
            if existing_email_user and not existing_email_user.is_verified:
                existing_email_user.delete()

            # Удаляем старый неверифицированный аккаунт с таким телефоном
            if phone:
                existing_phone_user = CustomUser.objects.filter(phone=phone).first()
                if existing_phone_user and not existing_phone_user.is_verified:
                    existing_phone_user.delete()

            try:
                # Создаём нового пользователя
                user = CustomUser.objects.create_user(email=email, phone=phone, password=password, first_name=first_name)

                # Создаём и отправляем код подтверждения
                code = VerificationCode.generate_code()
                VerificationCode.objects.create(user=user, code=code)

                send_mail(
                    'Підтвердження реєстрації',
                    f'Ваш код для підтвердження: {code}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email]
                )

                # Сохраняем id пользователя в сессии для последующего подтверждения
                request.session['verify_user_id'] = user.id

                messages.success(request, 'Код підтвердження було надіслано на вашу пошту.')

                return redirect('verify_email')

            except IntegrityError:
                form.add_error(None, 'Користувач з таким email або телефоном вже існує.')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            ident = form.cleaned_data['identifier']
            password = form.cleaned_data['password']

            # Пробуем по email
            user = authenticate(request, username=ident, password=password)

            # Если не получилось — пробуем по телефону
            if user is None:
                try:
                    user_obj = CustomUser.objects.get(phone=ident)
                    user = authenticate(request, username=user_obj.email, password=password)
                except CustomUser.DoesNotExist:
                    user = None

            if user is not None:
                if not user.is_verified:
                    request.session['verify_user_id'] = user.id
                    messages.warning(request, 'Підтвердіть ваш email для входу.')
                    return redirect('verify_email')

                # 🛒 Перенос корзины из сессии
                session_id = request.session.session_key
                guest_cart = Cart.objects.filter(session_id=session_id).first()
                user_cart, _ = Cart.objects.get_or_create(user=user)

                if guest_cart and guest_cart != user_cart:
                    for item in guest_cart.items.all():
                        existing = user_cart.items.filter(
                            product=item.product,
                            variant=item.variant
                        ).first()
                        if existing:
                            existing.quantity += item.quantity
                            existing.save()
                        else:
                            item.cart = user_cart
                            item.save()
                    guest_cart.delete()

                login(request, user)
                return redirect('welcome')
            else:
                messages.error(request, 'Невірні дані або пароль.')
                return redirect('login')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        request.session.flush()
    return redirect('welcome')


def password_reset_request_view(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = CustomUser.objects.filter(email=email).first()
            if user:
                code = VerificationCode.generate_code()
                VerificationCode.objects.create(user=user, code=code)
                send_mail(
                    'Скидання пароля',
                    f'Ваш код: {code}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email]
                )
                request.session['reset_user_id'] = user.id
                return redirect('password_reset_code')
    else:
        form = PasswordResetRequestForm()
    return render(request, 'accounts/password_reset_request.html', {'form': form})


def password_reset_code_view(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('login')

    user = CustomUser.objects.get(id=user_id)

    if request.method == 'POST':
        if 'resend' in request.POST:
            last_code = VerificationCode.objects.filter(user=user).order_by('-created_at').first()
            if last_code and timezone.now() - last_code.created_at < timedelta(minutes=1):
                messages.warning(request, 'Зачекайте хвилину перед повторною відправкою коду.')
            else:
                VerificationCode.objects.filter(user=user).delete()
                new_code = VerificationCode.generate_code()
                VerificationCode.objects.create(user=user, code=new_code)
                send_mail(
                    'Новий код для скидання пароля',
                    f'Ваш новий код: {new_code}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email]
                )
                messages.success(request, 'Новий код було надіслано на вашу пошту.')
            form = PasswordResetCodeForm()
            return render(request, 'accounts/password_reset_code.html', {'form': form})

        form = PasswordResetCodeForm(request.POST)
        if form.is_valid():
            entered_code = form.cleaned_data['code']
            code_obj = VerificationCode.objects.filter(user=user, code=entered_code).first()
            if code_obj and not code_obj.is_expired():
                code_obj.delete()
                request.session['allow_password_change'] = True
                return redirect('set_new_password')
            else:
                form.add_error('code', 'Невірний або прострочений код.')
    else:
        form = PasswordResetCodeForm()

    return render(request, 'accounts/password_reset_code.html', {'form': form})



def password_reset_new_password_view(request):
    user_id = request.session.get('reset_user_id')
    if not request.session.get('allow_password_change'):
        return redirect('login')
    user = CustomUser.objects.get(id=user_id)
    if request.method == 'POST':
        form = SetNewPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            del request.session['reset_user_id']
            del request.session['allow_password_change']
            messages.success(request, 'Пароль змінено. Увійдіть заново.')
            return redirect('login')
    else:
        form = SetNewPasswordForm(user)
    return render(request, 'accounts/password_reset_new.html', {'form': form})

def verify_email_view(request):
    user_id = request.session.get('verify_user_id')
    if not user_id:
        return redirect('register')

    user = CustomUser.objects.get(id=user_id)

    if request.method == 'POST':
        if 'resend' in request.POST:
            last_code = VerificationCode.objects.filter(user=user).order_by('-created_at').first()
            if last_code and timezone.now() - last_code.created_at < timedelta(minutes=1):
                messages.warning(request, 'Зачекайте хвилину перед повторною відправкою коду.')
            else:
                VerificationCode.objects.filter(user=user).delete()
                new_code = VerificationCode.generate_code()
                VerificationCode.objects.create(user=user, code=new_code)
                send_mail(
                    'Новий код підтвердження',
                    f'Ваш новий код: {new_code}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email]
                )
                messages.success(request, 'Новий код було надіслано на вашу пошту.')
            form = PasswordResetCodeForm()
            return render(request, 'accounts/verify_email.html', {'form': form})

        form = PasswordResetCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            code_obj = VerificationCode.objects.filter(user=user, code=code).first()
            if code_obj and not code_obj.is_expired():
                code_obj.delete()
                user.is_verified = True
                user.save()
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                del request.session['verify_user_id']
                messages.success(request, 'Підтвердження пройшло успішно.')
                return redirect('welcome')
            else:
                form.add_error('code', 'Невірний або прострочений код.')
    else:
        form = PasswordResetCodeForm()

    return render(request, 'accounts/verify_email.html', {'form': form})


@login_required
def user_cabinet_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/user_cabinet.html', {
        'user': request.user,
        'orders': orders,
    })

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'phone']
        labels = {
            'first_name': "Ім’я",
            'phone': "Телефон",
        }

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профіль успішно оновлено.")
            return redirect('user_cabinet')
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'accounts/edit_profile.html', {'form': form})

def google_login_complete_safe(request, backend):
    try:
        return complete(request, backend)
    except AuthCanceled:
        return redirect('/login/?cancel=1')