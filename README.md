🟤 Gorishnik
Проект для интернет-магазина с орехами и сухофруктами.

🔧 Стек технологий
Python 3.12

Django 5.1

PostgreSQL

Docker / Docker Compose

OAuth2 (Google)

Email верификация

LiqPay (тестовая интеграция)

🚀 Запуск проекта в Docker
1. Установи Docker:
https://www.docker.com/products/docker-desktop/

2. Клонируй репозиторий и перейди в папку проекта:
bash
Копировать
Редактировать
git clone https://github.com/Artur-Kalinenko/Gorishnik.git
cd Gorishnik
3. Создай .env файл рядом с docker-compose.yml:
env
Копировать
Редактировать
DJANGO_SECRET_KEY=...

DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_secure_password
DB_HOST=db
DB_PORT=5432

EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your_password

LIQPAY_PUBLIC_KEY=sandbox_key
LIQPAY_PRIVATE_KEY=sandbox_private
LIQPAY_SANDBOX=True

GOOGLE_OAUTH2_KEY=your_google_client_id
GOOGLE_OAUTH2_SECRET=your_google_secret
4. Собери и запусти контейнеры:
bash
Копировать
Редактировать
docker compose up --build
5. Выполни миграции и создай суперпользователя:
bash
Копировать
Редактировать
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
🌐 Доступ к сайту
Главная: http://localhost:8000/

Админка: http://localhost:8000/admin/

Логин через Google: настраивается через OAuth2

🕒 Автоматическая очистка корзины (cron)
Что делает:

Удаляет CartItem, не обновлявшиеся более 24 часов

Удаляет Cart гостей, неактивные более 2 суток

Удаляет Cart авторизованных пользователей, неактивные более 30 дней

Как работает:

Запускается каждый день в 03:00 (по системному времени)

Настроено с помощью django-crontab

✅ Проверка/активация cron:
Убедись, что библиотека установлена:

bash
Копировать
Редактировать
pip install django-crontab
Добавь в settings.py:

python
Копировать
Редактировать
INSTALLED_APPS += ['django_crontab']

CRONJOBS = [
    ('0 3 * * *', 'django.core.management.call_command', ['clear_cart']),
]
Запуск задачи:

bash
Копировать
Редактировать
python manage.py crontab add
Проверка:

bash
Копировать
Редактировать
python manage.py crontab show
🔁 Важно: при переносе проекта на другой сервер — повтори crontab add.

📦 Статика
Для сбора статики:

bash
Копировать
Редактировать
docker compose exec web python manage.py collectstatic
