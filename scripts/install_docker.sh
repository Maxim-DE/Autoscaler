#!/bin/bash

# Файл: install_docker.sh

set -e  # Прерывать выполнение при ошибке

echo "=== Начинаем установку Docker ==="

# Обновляем список пакетов
echo "1. Обновляем список пакетов..."
sudo apt-get update

# Устанавливаем необходимые пакеты для использования репозиторий через HTTPS
echo "2. Устанавливаем зависимости..."
sudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common -y

# Добавляем официальный GPG ключ Docker
echo "3. Добавляем GPG ключ Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# Добавляем Docker репозиторий
echo "4. Добавляем Docker репозиторий..."
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable" -y

# Обновляем список пакетов с новым репозиторием
echo "5. Обновляем список пакетов с Docker репозиторием..."
sudo apt-get update

# Устанавливаем Docker
echo "6. Устанавливаем Docker..."
sudo apt-get install docker-ce docker-ce-cli containerd.io -y

echo "=== Установка Docker завершена! ==="

# Проверяем установку
echo "Проверяем версию Docker:"
docker --version