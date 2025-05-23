                                        🌰 GORISNIK_UA 🌰

🥜Gorishnik — це інтернет-магазин оріхів, сухофруктів та смаколиків на Django.


<--- 🔧Технології --->
Python 3.12
Django 5.1
PostgreSQL
Docker / Docker Compose
OAuth2 (Google)
Email-верифікація
LiqPay (тестова інтеграція)
Нова Пошта api (тестова інтеграція)
Автоочистка корзин, кодів і неверифікованих користувачів (cron)


<--- 🚀Запуск проекту в Docker --->
1. Установи Docker: https://www.docker.com/products/docker-desktop/

2. Клонуй репозиторій:
git clone https://github.com/Artur-Kalinenko/Gorishnik.git
cd Gorishnik

3. Створи .env файл:
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

NOVA_POSHTA_API_KEY=nova-poshta-api

4. Собери і запусти контейнери:
docker compose up --build

5. Виконай міграції та створи суперкористувача:
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser


<--- 🌐Доступ до сайту --->
Головна: http://localhost:8000/
Адмінка: http://localhost:8000/admin/


<--- 🕒Автоочистка (крон) --->
Що очищається:
- заброшені CartItem через 24 год.
- корзини гостей через 48 год.
- корзини авториз. користувачів через 30 діб
- верифікаційні коди старше 30 хв.
- неверифіковані користувачі, що не підтвердили email за 24 год.

Спосіб налаштування: django-crontab
CRONJOBS = [
    ('0 3 * * *', 'django.core.management.call_command', ['clear_cart']),
    ('0 4 * * *', 'django.core.management.call_command', ['clear_verification_codes']),
    ('0 5 * * *', 'django.core.management.call_command', ['delete_unverified_users']),
]

Повторна активація:
python manage.py crontab remove
python manage.py crontab add
python manage.py crontab show


<--- 📦Статика --->
Сбір статичних файлів (при деплої):
docker compose exec web python manage.py collectstatic


📍 Питання? Звертайся до розробника: 
Telegram: @arturkalinenko