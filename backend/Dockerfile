FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости для сборки зависимостей (например для psycopg2)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements
COPY requirements.txt .

# Устанавливаем python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Открываем порт Django (если понадобится)
EXPOSE 8000

# Стандартная команда (перезапишется в docker-compose для runserver, celery и beat)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
