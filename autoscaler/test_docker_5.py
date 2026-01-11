#!/usr/bin/env python3
import os
import docker

print("Тест docker==5.0.3")
print("=" * 50)

# 1. Очищаем
print("\n1. Очищаем переменные...")
for var in ['DOCKER_HOST', 'DOCKER_TLS_VERIFY', 'DOCKER_CERT_PATH']:
    if var in os.environ:
        print(f"   Удаляю {var}={os.environ[var]}")
        del os.environ[var]

# 2. Устанавливаем правильную
print("\n2. Устанавливаю DOCKER_HOST='unix://var/run/docker.sock'")
os.environ['DOCKER_HOST'] = 'unix://var/run/docker.sock'

# 3. Пробуем подключиться
print("\n3. Пробую docker.from_env()...")
try:
    client = docker.from_env()
    ver = client.version()
    print(f"   ✓ Успешно! Docker {ver['Version']}")
    print(f"   ✓ Swarm: {client.info().get('Swarm', {}).get('LocalNodeState')}")
except Exception as e:
    print(f"   ✗ Ошибка: {e}")

# 4. Пробуем напрямую
print("\n4. Пробую DockerClient(base_url='unix://var/run/docker.sock')...")
try:
    client2 = docker.DockerClient(base_url='unix://var/run/docker.sock')
    ver2 = client2.version()
    print(f"   ✓ Успешно! Docker {ver2['Version']}")
except Exception as e:
    print(f"   ✗ Ошибка: {e}")

print("\n" + "=" * 50)
