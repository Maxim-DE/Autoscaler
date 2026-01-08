

Команда на сборку образа 
docker build -t web-service .

# Запустите контейнер
docker run -p 4000:4000 -e HOSTNAME=my-container nodejs-app
# Запустите все сервисы
docker-compose up



После запуска откройте браузер и проверьте эндпоинты:

    
Делаем первый запрос 
http://45.12.19.151/memory-heavy  
Получаем нагрузку только на 1 реплику 
Делаем запрос второй получаем нагрузку на вторую реплику 


Запрос выделит 1 МБ памяти и освободит черзе 1500 мс
http://45.12.19.151/memory-fast-heavy


    


    Главная страница: http://localhost:4000/

    Health check: http://localhost:4000/health

    Метрики: http://localhost:4000/metrics

    Информация о памяти: http://localhost:4000/metrics/memory-info

    CPU нагрузка: http://localhost:4000/heavy

    Медленный запрос: http://localhost:4000/slow?delay=2000

    Отладка контейнера: http://localhost:4000/metrics/debug-container