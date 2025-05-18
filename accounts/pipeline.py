# Помечает пользователя как верифицированного после успешной авторизации через соцсеть
def set_verified(backend, user, *args, **kwargs):
    if user and not user.is_verified:
        user.is_verified = True
        user.save()