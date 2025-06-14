FROM python:3.12

# Отключаем pyc и буферизацию
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Создаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем cron и клиент PostgreSQL, качаем библиотеки Python
RUN apt-get update \
    && apt-get install -y cron postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Команда по умолчанию (будет переопределена docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
