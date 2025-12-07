

Запуск стека 
```
docker stack deploy -c Autoscaler/monitoring/monitoring-stack.yml monitoring
```

Проверка 
```
docker stack services monitoring
```

```
docker service scale web_app=5
```

Удалить стек 
```
docker stack rm monitoring
```

```
docker stack ls
```
