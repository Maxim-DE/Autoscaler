

Команда на сборку образа 
docker build -t web-service .

# Запустите контейнер
docker run -p 4000:4000 -e HOSTNAME=my-container nodejs-app
# Запустите все сервисы
docker-compose up



После запуска откройте браузер и проверьте эндпоинты:

    Главная страница: http://localhost:4000/

    Health check: http://localhost:4000/health

    Метрики: http://localhost:4000/metrics

    Информация о памяти: http://localhost:4000/metrics/memory-info

    CPU нагрузка: http://localhost:4000/heavy

    Медленный запрос: http://localhost:4000/slow?delay=2000

    Отладка контейнера: http://localhost:4000/metrics/debug-container