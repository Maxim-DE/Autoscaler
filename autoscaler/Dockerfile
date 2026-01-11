FROM python:3.9-slim

# Устанавливаем минимальные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем основной скрипт
COPY Scaler-1.0.1.py .

# Создаем папку для логов (опционально)
RUN mkdir -p /app/logs

# Запускаем скрипт
# Используем -u для unbuffered output
CMD ["python", "-u", "Scaler-1.0.1.py"]
# CMD ["python", "Scaler-1.0.1.py"]