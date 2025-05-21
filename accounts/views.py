from django.shortcuts import render, redirect
from .forms import (
    RegistrationForm,
    LoginForm,
    PasswordResetRequestForm,
    PasswordResetCodeForm,
    SetNewPasswordForm,
    ChangeEmailForm,
    CustomPasswordChangeForm
)
from favorites.models import Favorite
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
from cart.models import Cart, CartItem
from orders.models import Order
from social_core.exceptions import AuthCanceled
from social_django.views import complete
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from itertools import zip_longest
from django.contrib.auth import update_session_auth_hash
from django.utils.dateparse import parse_datetime
# from django.http import HttpResponseRedirect
# from django.urls import reverse

# Регистрация нового пользователя
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
                VerificationCode.objects.create(user=user, code=code, last_sent_at=timezone.now() - timedelta(minutes=1))

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

# Авторизация по email или телефону + перенос корзины из сессии
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

                # Убеждаемся, что у сессии есть ключ
                if not request.session.session_key:
                    request.session.create()

                session_id = request.session.session_key

                # Перенос корзины
                guest_cart = Cart.objects.filter(session_id=session_id, user__isnull=True).first()
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
                            CartItem.objects.create(
                                cart=user_cart,
                                product=item.product,
                                quantity=item.quantity,
                                variant=item.variant
                            )
                    guest_cart.delete()

                login(request, user)
                return redirect('welcome')
            else:
                messages.error(request, 'Невірні дані або пароль.')
                return redirect('login')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

# Выход из аккаунта
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        request.session.flush()
    return redirect('welcome')


# Запрос на сброс пароля (отправка кода)
def password_reset_request_view(request):
    if not request.session.session_key:
        request.session.create()

    request.session.pop('reset_user_id', None)
    request.session.pop('allow_password_change', None)

    if request.method == 'POST': # Генерация и отправка кода на email
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = CustomUser.objects.filter(email=email).first()
            if user:
                code = VerificationCode.generate_code()
                VerificationCode.objects.create(user=user, code=code, last_sent_at=timezone.now() - timedelta(minutes=1))
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


# Ввод кода для сброса пароля
def password_reset_code_view(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('login')

    user = CustomUser.objects.get(id=user_id)

    if request.method == 'POST':
        if 'resend' in request.POST:
            session_data = request.session.get('reset_password', {})
            sent_at_str = session_data.get('sent_at')
            is_first = session_data.get('is_first', True)

            if not is_first and sent_at_str:
                sent_at = parse_datetime(sent_at_str)
                now = timezone.now()
                seconds_passed = (now - sent_at).total_seconds()
                if seconds_passed < 60:
                    messages.warning(request, f'Зачекайте {int(60 - seconds_passed)} сек. перед повторною відправкою коду.')
                    form = PasswordResetCodeForm()
                    return render(request, 'accounts/password_reset_code.html', {'form': form})

            new_code = VerificationCode.generate_code()
            session_data = {
                'code': new_code,
                'sent_at': timezone.now().isoformat(),
                'is_first': False,
            }
            request.session['reset_password'] = session_data

            send_mail(
                'Новий код для скидання пароля',
                f'Ваш новий код: {new_code}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            )
            messages.success(request, 'Новий код було надіслано на вашу пошту.')
            form = PasswordResetCodeForm()

        else:
            form = PasswordResetCodeForm(request.POST)
            if form.is_valid():
                code_entered = form.cleaned_data['code']
                session_data = request.session.get('reset_password')
                if session_data and code_entered == session_data['code']:
                    request.session['allow_password_change'] = True
                    return redirect('set_new_password')
                else:
                    form.add_error('code', 'Невірний або прострочений код.')
    else:
        # Первая отправка
        new_code = VerificationCode.generate_code()
        session_data = {
            'code': new_code,
            'sent_at': timezone.now().isoformat(),
            'is_first': True,
        }
        request.session['reset_password'] = session_data

        send_mail(
            'Код для скидання пароля',
            f'Ваш код: {new_code}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )
        messages.info(request, 'Код було надіслано на вашу пошту.')
        form = PasswordResetCodeForm()

    return render(request, 'accounts/password_reset_code.html', {'form': form})

# Установка нового пароля после подтверждения кода
def password_reset_new_password_view(request):
    user_id = request.session.get('reset_user_id')
    if not request.session.get('allow_password_change'):
        return redirect('login')
    user = CustomUser.objects.get(id=user_id)
    if request.method == 'POST':
        form = SetNewPasswordForm(user, request.POST)
        if form.is_valid(): # Очистка сессии и редирект на логин
            form.save()
            del request.session['reset_user_id']
            del request.session['allow_password_change']
            messages.success(request, 'Пароль змінено. Увійдіть заново.')
            return redirect('login')
    else:
        form = SetNewPasswordForm(user)
    return render(request, 'accounts/password_reset_new.html', {'form': form})

# Подтверждение email при регистрации
def verify_email_view(request):
    user_id = request.session.get('verify_user_id')
    if not user_id:
        return redirect('register')

    user = CustomUser.objects.get(id=user_id)

    if request.method == 'POST':
        if 'resend' in request.POST:
            session_data = request.session.get('verify_email_data', {})
            sent_at_str = session_data.get('sent_at')
            is_first = session_data.get('is_first', True)

            if not is_first and sent_at_str:
                sent_at = parse_datetime(sent_at_str)
                now = timezone.now()
                seconds_passed = (now - sent_at).total_seconds()

                if seconds_passed < 60:
                    messages.warning(request, f'Зачекайте {int(60 - seconds_passed)} сек. перед повторною відправкою коду.')
                    form = PasswordResetCodeForm()
                    return render(request, 'accounts/verify_email.html', {'form': form})

            new_code = VerificationCode.generate_code()
            VerificationCode.objects.create(user=user, code=new_code, last_sent_at=timezone.now())

            # Обновляем сессию
            request.session['verify_email_data'] = {
                'sent_at': timezone.now().isoformat(),
                'is_first': False
            }

            send_mail(
                'Новий код підтвердження',
                f'Ваш новий код: {new_code}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            )
            messages.success(request, 'Новий код було надіслано на вашу пошту.')
            form = PasswordResetCodeForm()
        else:
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
                    request.session.pop('verify_email_data', None)
                    messages.success(request, 'Підтвердження пройшло успішно.')
                    return redirect('welcome')
                else:
                    form.add_error('code', 'Невірний або прострочений код.')
    else:
        # Первая загрузка — установить таймер
        request.session['verify_email_data'] = {
            'sent_at': timezone.now().isoformat(),
            'is_first': True
        }
        form = PasswordResetCodeForm()

    return render(request, 'accounts/verify_email.html', {'form': form})

# Хелпер: разбивает список на подсписки по size элементов
def chunked(iterable, size):
    it = iter(iterable)
    return list(zip_longest(*[it] * size, fillvalue=None))

@login_required
def user_cabinet_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    favorites = Favorite.objects.filter(user=request.user).select_related('product')
    favorites_ids = list(favorites.values_list('product_id', flat=True))
    grouped_favorites = chunked(favorites, 3)  # для карусели по 3 товара

    if request.session.get('change_email'):
        messages.warning(request,
                         'Ви намагалися змінити адресу електронної пошти, але не пройшли веріфікацію, будь ласка, спробуйте ще раз.')
        del request.session['change_email']

    return render(request, 'accounts/user_cabinet.html', {
        'user': request.user,
        'orders': orders,
        'favorites': favorites,
        'favorites_ids': favorites_ids,
        'grouped_favorites': grouped_favorites,
    })

# Форма редактирования профиля
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'phone']
        labels = {
            'first_name': "Ім’я",
            'phone': "Телефон",
        }

# Редактирование профиля пользователя
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

# Обработка отмены логина через Google
def google_login_complete_safe(request, backend):
    try:
        return complete(request, backend)
    except AuthCanceled:
        return redirect('/login/?cancel=1')

# Сохранение session key
@require_POST
@csrf_exempt
def save_pre_social_session(request):
    request.session['pre_social_auth_session_key'] = request.session.session_key or request.session.create()
    return JsonResponse({'status': 'ok'})


@login_required
def change_email_request_view(request):
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST)
        if form.is_valid():
            new_email = form.cleaned_data['new_email']
            code = VerificationCode.generate_code()

            # Первая отправка: флаг is_first = True
            request.session['change_email'] = {
                'new_email': new_email,
                'code': code,
                'sent_at': timezone.now().isoformat(),
                'is_first': True,
            }

            send_mail(
                'Підтвердження нової електронної пошти',
                f'Ваш код підтвердження: {code}',
                settings.DEFAULT_FROM_EMAIL,
                [new_email]
            )

            messages.info(request, 'Код підтвердження надіслано на нову електронну адресу.')
            return redirect('confirm_change_email')
    else:
        form = ChangeEmailForm()

    return render(request, 'accounts/change_email_request.html', {'form': form})

@login_required
def confirm_change_email_view(request):
    session_data = request.session.get('change_email')
    if not session_data:
        messages.warning(request, 'Ви не ініціювали зміну електронної пошти.')
        return redirect('user_cabinet')

    if request.method == 'POST':
        if 'resend' in request.POST:
            sent_at_str = session_data.get('sent_at')
            is_first = session_data.get('is_first', False)

            # Разрешаем только первую отправку без ограничений
            if not is_first:
                sent_at = parse_datetime(sent_at_str)
                now = timezone.now()
                seconds_passed = (now - sent_at).total_seconds()

                if seconds_passed < 60:
                    messages.warning(request, f'Зачекайте {int(60 - seconds_passed)} сек. перед повторною відправкою коду.')
                    form = PasswordResetCodeForm()
                    return render(request, 'accounts/confirm_change_email.html', {'form': form})

            # Если прошло 60 сек или это первая отправка — отправляем код
            new_code = VerificationCode.generate_code()
            session_data = session_data.copy()
            session_data['code'] = new_code
            session_data['sent_at'] = timezone.now().isoformat()
            session_data['is_first'] = False
            request.session['change_email'] = session_data

            send_mail(
                'Новий код підтвердження',
                f'Ваш код: {new_code}',
                settings.DEFAULT_FROM_EMAIL,
                [session_data['new_email']]
            )
            messages.success(request, 'Новий код надіслано на вашу пошту.')
            form = PasswordResetCodeForm()
        else:
            form = PasswordResetCodeForm(request.POST)
            if form.is_valid():
                code_entered = form.cleaned_data['code']
                if code_entered == session_data['code']:
                    request.user.email = session_data['new_email']
                    request.user.save()
                    del request.session['change_email']
                    messages.success(request, 'Email успішно змінено.')
                    return redirect('user_cabinet')
                else:
                    form.add_error('code', 'Невірний код.')
    else:
        form = PasswordResetCodeForm()

    return render(request, 'accounts/confirm_change_email.html', {'form': form})



@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password1']
            code = VerificationCode.generate_code()

            # Сохраняем пароль и код в сессии
            request.session['change_password'] = {
                'code': code,
                'password': new_password,
                'sent_at': timezone.now().isoformat(),
                'is_first': True,
            }

            send_mail(
                'Підтвердження зміни пароля',
                f'Ваш код підтвердження: {code}',
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email]
            )

            messages.info(request, 'Код підтвердження було надіслано на ваш email.')
            return redirect('confirm_change_password')
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'accounts/change_password.html', {'form': form})

@login_required
def confirm_change_password_view(request):
    session_data = request.session.get('change_password')
    if not session_data:
        messages.warning(request, 'Ви не ініціювали зміну пароля.')
        return redirect('user_cabinet')

    if request.method == 'POST':
        if 'resend' in request.POST:
            sent_at_str = session_data.get('sent_at')
            is_first = session_data.get('is_first', False)

            # Проверка: если это не первая отправка — проверяем таймер
            if not is_first:
                sent_at = parse_datetime(sent_at_str)
                now = timezone.now()
                seconds_passed = (now - sent_at).total_seconds()

                if seconds_passed < 60:
                    messages.warning(
                        request,
                        f'Зачекайте {int(60 - seconds_passed)} сек. перед повторною відправкою коду.'
                    )
                    form = PasswordResetCodeForm()
                    return render(request, 'accounts/confirm_change_password.html', {'form': form})

            # Генерация нового кода
            new_code = VerificationCode.generate_code()
            session_data = session_data.copy()
            session_data['code'] = new_code
            session_data['sent_at'] = timezone.now().isoformat()
            session_data['is_first'] = False
            request.session['change_password'] = session_data

            send_mail(
                'Новий код підтвердження',
                f'Ваш новий код: {new_code}',
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email]
            )
            messages.success(request, 'Новий код було надіслано на вашу пошту.')
            form = PasswordResetCodeForm()
        else:
            form = PasswordResetCodeForm(request.POST)
            if form.is_valid():
                code_entered = form.cleaned_data['code']
                if code_entered == session_data['code']:
                    request.user.set_password(session_data['password'])
                    request.user.save()
                    update_session_auth_hash(request, request.user)
                    del request.session['change_password']
                    messages.success(request, 'Пароль успішно змінено.')
                    return redirect('user_cabinet')
                else:
                    form.add_error('code', 'Невірний код.')
    else:
        form = PasswordResetCodeForm()

    return render(request, 'accounts/confirm_change_password.html', {'form': form})