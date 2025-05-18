# Dockerfile

FROM python:3.12

# Отключаем pyc и буферизацию
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Создаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Команда по умолчанию (будет переопределена docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]