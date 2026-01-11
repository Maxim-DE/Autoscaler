#!/usr/bin/env python3
# Сразу выводим что скрипт запустился
import sys
import os
print("🚀 Autoscaler запущен", file=sys.stderr)
print(f"Python: {sys.version}", file=sys.stderr)
sys.stderr.flush()

import time
import json
import requests
from typing import List, Dict, Any, Optional
from docker import DockerClient
from docker.errors import DockerException, APIError

# Отключаем буферизацию
sys.stdout.reconfigure(line_buffering=True)  # Python 3.7+
# Или
os.environ['PYTHONUNBUFFERED'] = '1'

# Перенаправляем stderr в stdout для Docker
if not sys.stderr.isatty():
    sys.stderr = sys.stdout

# Конфигурация
LOOP = os.environ.get('LOOP', 'yes')
CPU_PERCENTAGE_UPPER_LIMIT = int(os.environ.get('CPU_PERCENTAGE_UPPER_LIMIT', '85'))
CPU_PERCENTAGE_LOWER_LIMIT = int(os.environ.get('CPU_PERCENTAGE_LOWER_LIMIT', '25'))
CHECK_INTERVAL = int(os.environ.get('CHECK_INTERVAL', '10'))

# URL Prometheus (ваш конкретный адрес)
PROMETHEUS_URL = os.environ.get('PROMETHEUS_URL', 'http://45.84.224.156:9000')
PROMETHEUS_API = f"{PROMETHEUS_URL}/api/v1/query"  # Для API v1


# Правильный запрос для Prometheus
# PROMETHEUS_QUERY = os.environ.get(
#     'PROMETHEUS_QUERY',
#     'sum(rate(container_cpu_usage_seconds_total{container_label_com_docker_swarm_task_name=~".+"}[1m])) by (container_label_com_docker_swarm_service_name) * 100'
# )


# Правильный запрос с учетом лимитов
# PROMETHEUS_QUERY = '''
# rate(container_cpu_usage_seconds_total{name=~"my-app.*"}[1m]) * 100
# '''

# PROMETHEUS_QUERY = '''
# # Средняя загрузка CPU по всем репликам сервиса за 1 минут
# avg(
#   rate(container_cpu_usage_seconds_total{container_label_com_docker_swarm_service_name="my-app_my-app"}[1m])
# ) by (container_label_com_docker_swarm_service_name)
# * 100
# '''

# Только контейнеры в состоянии "running"
PROMETHEUS_QUERY = '''
rate(container_cpu_usage_seconds_total{
  node_name=~"Worker.*",
  container_label_com_docker_stack_namespace="my-app",
  image!=""
}[1m]) * 100
'''

# По cgroup (система, docker, systemd)
# sum by (id) (
#   rate(container_cpu_usage_seconds_total{
#     node_name="Worker2"
#   }[1m])
# ) * 100


# Полная нагрузка на сервер 2
# sum by (node_name) (
#   rate(container_cpu_usage_seconds_total{
#     node_name="Worker2",
#     id="/"
#   }[1m])
# ) * 100

# Альтернатива: использовать max вместо sum для отдельных контейнеров
PROMETHEUS_QUERY_MAX = '''
max(
  100 * rate(container_cpu_usage_seconds_total{
    container_label_com_docker_swarm_task_name=~".+"
  }[1m])
  /
  (
    container_spec_cpu_quota{
      container_label_com_docker_swarm_task_name=~".+"
    } 
    / 
    container_spec_cpu_period{
      container_label_com_docker_swarm_task_name=~".+"
    }
  )
) by (container_label_com_docker_swarm_service_name)
'''


print(f"DOCKER_HOST env: {os.getenv('DOCKER_HOST')}")
print(f"Checking Docker socket: {os.path.exists('/var/run/docker.sock')}")

print(f"Prometheus URL: {PROMETHEUS_URL}")
print(f"Prometheus API endpoint: {PROMETHEUS_API}")
print(f"Query: {PROMETHEUS_QUERY[:100]}..." if len(PROMETHEUS_QUERY) > 100 else f"Query: {PROMETHEUS_QUERY}")


class DockerSwarmAutoscaler:
    def __init__(self):
        """Инициализация Docker клиента"""
        try:
            # ОЧИЩАЕМ ВСЕ ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ которые могут мешать
            import os
            problematic_vars = ['DOCKER_HOST', 'DOCKER_TLS_VERIFY', 'DOCKER_CERT_PATH']
            for var in problematic_vars:
                if var in os.environ:
                    print(f"⚠ Удаляю проблемную переменную: {var}={os.environ[var]}")
                    del os.environ[var]
            
            print("Подключение к Docker socket...")
            
            # Пробуем подключиться
            try:
                self.client = DockerClient(base_url='unix://var/run/docker.sock')  # 2 слеша!
                print("Успешно подключено к Docker")
                
                # Проверяем что работает
                version = self.client.version()
                print(f"Docker версия: {version.get('Version', 'N/A')}")
                
            except Exception as e:
                print(f"Ошибка при подключении: {e}")
                raise
                
        except Exception as e:
            print(f"Ошибка инициализации Docker клиента: {e}")
            import traceback
            traceback.print_exc()  # Это покажет полный стек вызовов
            raise  
    # def __init__(self):
    #     """Инициализация Docker клиента"""
    #     try:
    #         # Отладочная информация
    #         import os
    #         docker_socket = '/var/run/docker.sock'
    #         print(f"Docker socket exists: {os.path.exists(docker_socket)}")
    #         print(f"Docker socket permissions: {oct(os.stat(docker_socket).st_mode) if os.path.exists(docker_socket) else 'N/A'}")
    #         print(f"DOCKER_HOST env: {os.getenv('DOCKER_HOST')}")
            
    #         # Пробуем разные варианты подключения
    #         docker_host = os.getenv('DOCKER_HOST')
    #         if docker_host:
    #             print(f"Using DOCKER_HOST: {docker_host}")
    #             self.client = DockerClient(base_url=docker_host)
    #         else:
    #             print("Using default Docker socket")
    #             self.client = DockerClient.from_env()
            
    #         print("Успешно подключено к Docker")
            
    #         # Проверяем что это Swarm
    #         info = self.client.info()
    #         print(f"Swarm node ID: {info.get('Swarm', {}).get('NodeID', 'N/A')[:12]}")
            
    #     except DockerException as e:
    #         print(f"Ошибка подключения к Docker: {e}")
    #         # Попробуем альтернативный способ
    #         try:
    #             print("Пробуем альтернативное подключение...")
    #             self.client = DockerClient(base_url='unix://var/run/docker.sock')
    #             print("Успешно через unix://var/run/docker.sock")
    #         except Exception as e2:
    #             print(f"И это не помогло: {e2}")
    #             raise
    
    def get_high_cpu_services(self, prometheus_results: Dict[str, Any]) -> List[str]:
        """Получить сервисы с высокой загрузкой CPU"""
        services = []
        if 'data' in prometheus_results and 'result' in prometheus_results['data']:
            for result in prometheus_results['data']['result']:
                if 'value' in result and len(result['value']) > 1:
                    try:
                        cpu_usage = float(result['value'][1])
                        if cpu_usage > CPU_PERCENTAGE_UPPER_LIMIT:
                            service_name = result['metric'].get('container_label_com_docker_swarm_service_name')
                            if service_name and service_name not in services:
                                services.append(service_name)
                    except (ValueError, TypeError):
                        continue
        return services
    
    def get_all_services(self, prometheus_results: Dict[str, Any]) -> List[str]:
        """Получить все сервисы из результатов Prometheus"""
        services = []
        if 'data' in prometheus_results and 'result' in prometheus_results['data']:
            for result in prometheus_results['data']['result']:
                service_name = result['metric'].get('container_label_com_docker_swarm_service_name')
                if service_name and service_name not in services:
                    services.append(service_name)
        return services
    
    def get_low_cpu_services(self, prometheus_results: Dict[str, Any]) -> List[str]:
        """Получить сервисы с низкой загрузкой CPU"""
        services = []
        if 'data' in prometheus_results and 'result' in prometheus_results['data']:
            for result in prometheus_results['data']['result']:
                if 'value' in result and len(result['value']) > 1:
                    try:
                        cpu_usage = float(result['value'][1])
                        if cpu_usage < CPU_PERCENTAGE_LOWER_LIMIT:
                            service_name = result['metric'].get('container_label_com_docker_swarm_service_name')
                            if service_name and service_name not in services:
                                services.append(service_name)
                    except (ValueError, TypeError):
                        continue
        return services
    
    def get_service_by_name(self, service_name: str):
        """Получить объект сервиса по имени"""
        try:
            services = self.client.services.list(filters={'name': service_name})
            return services[0] if services else None
        except APIError as e:
            print(f"Ошибка при получении сервиса {service_name}: {e}")
            return None
    
    def get_service_labels(self, service_name: str) -> Dict[str, str]:
        """Получить метки сервиса"""
        service = self.get_service_by_name(service_name)
        if service:
            return service.attrs['Spec']['Labels']
        return {}
    
    def get_service_replicas(self, service_name: str) -> Optional[int]:
        """Получить текущее количество реплик сервиса"""
        service = self.get_service_by_name(service_name)
        if service and 'Mode' in service.attrs['Spec']:
            if 'Replicated' in service.attrs['Spec']['Mode']:
                return service.attrs['Spec']['Mode']['Replicated']['Replicas']
        return None
    
    def default_scale(self, service_name: str) -> None:
        """Проверить и масштабировать сервис до значений по умолчанию"""
        try:
            service = self.get_service_by_name(service_name)
            if not service:
                print(f"Сервис {service_name} не найден")
                return
            
            labels = service.attrs['Spec']['Labels']
            auto_scale_label = labels.get('swarm.autoscaler')
            
            if auto_scale_label == 'true':
                print(f"Service {service_name} has an autoscale label.")
                
                # Получаем минимальное и максимальное количество реплик
                try:
                    replica_minimum = int(labels.get('swarm.autoscaler.minimum', 1))
                    replica_maximum = int(labels.get('swarm.autoscaler.maximum', 10))
                except ValueError:
                    print(f"Некорректные значения minimum/maximum для сервиса {service_name}")
                    return
                
                # Получаем текущее количество реплик
                current_replicas = service.attrs['Spec']['Mode']['Replicated']['Replicas']
                
                # Проверяем и масштабируем при необходимости
                if replica_minimum > current_replicas:
                    print(f"Service {service_name} is below the minimum. Scaling to the minimum of {replica_minimum}")
                    service.update(mode={'Replicated': {'Replicas': replica_minimum}})
                elif current_replicas > replica_maximum:
                    print(f"Service {service_name} is above the maximum. Scaling to the maximum of {replica_maximum}")
                    service.update(mode={'Replicated': {'Replicas': replica_maximum}})
            else:
                print(f"Service {service_name} does not have an autoscale label.")
                
        except (KeyError, APIError, DockerException) as e:
            print(f"Ошибка обработки сервиса {service_name}: {e}")
    
    def scale_down(self, service_name: str) -> None:
        """Уменьшить количество реплик сервиса"""
        try:
            service = self.get_service_by_name(service_name)
            if not service:
                return
            
            labels = service.attrs['Spec']['Labels']
            auto_scale_label = labels.get('swarm.autoscaler')
            
            if auto_scale_label == 'true':
                try:
                    replica_minimum = int(labels.get('swarm.autoscaler.minimum', 1))
                except ValueError:
                    print(f"Некорректное значение minimum для сервиса {service_name}")
                    return
                
                current_replicas = service.attrs['Spec']['Mode']['Replicated']['Replicas']
                new_replicas = current_replicas - 1
                
                if replica_minimum <= new_replicas:
                    print(f"Scaling down the service {service_name} to {new_replicas}")
                    service.update(mode={'Replicated': {'Replicas': new_replicas}})
                elif current_replicas == replica_minimum:
                    print(f"Service {service_name} has the minimum number of replicas.")
                    
        except (KeyError, APIError, DockerException) as e:
            print(f"Ошибка масштабирования сервиса {service_name} вниз: {e}")
    
    def scale_up(self, service_name: str) -> None:
        """Увеличить количество реплик сервиса"""
        try:
            service = self.get_service_by_name(service_name)
            if not service:
                return
            
            labels = service.attrs['Spec']['Labels']
            auto_scale_label = labels.get('swarm.autoscaler')
            
            if auto_scale_label == 'true':
                try:
                    replica_maximum = int(labels.get('swarm.autoscaler.maximum', 10))
                except ValueError:
                    print(f"Некорректное значение maximum для сервиса {service_name}")
                    return
                
                current_replicas = service.attrs['Spec']['Mode']['Replicated']['Replicas']
                new_replicas = current_replicas + 1
                
                if current_replicas == replica_maximum:
                    print(f"Service {service_name} already has the maximum of {replica_maximum} replicas")
                elif replica_maximum >= new_replicas:
                    print(f"Scaling up the service {service_name} to {new_replicas}")
                    service.update(mode={'Replicated': {'Replicas': new_replicas}})
                    
        except (KeyError, APIError, DockerException) as e:
            print(f"Ошибка масштабирования сервиса {service_name} вверх: {e}")
    
    def get_prometheus_data(self) -> Optional[Dict[str, Any]]:
        """Получить данные из Prometheus"""
        try:
            # ИСПРАВЛЕННЫЙ ВАРИАНТ 1: используем PROMETHEUS_API напрямую
            params = {'query': PROMETHEUS_QUERY}
            print(f"Запрос к Prometheus: {PROMETHEUS_API}")
            print(f"Query параметры: {params}")
            
            response = requests.get(PROMETHEUS_API, params=params, timeout=30)
            print(f"Статус ответа: {response.status_code}")
            
            response.raise_for_status()
            data = response.json()
            
            # Проверяем статус ответа Prometheus
            if data.get('status') != 'success':
                print(f"Ошибка Prometheus: {data.get('error', 'Unknown error')}")
                return None
                
            return data
            
        except requests.RequestException as e:
            print(f"Ошибка при запросе к Prometheus: {e}")
            return None
    
    def convert_prometheus_to_list(self,prometheus_data):
        """
        Извлекает загрузку CPU по нодам из результатов Prometheus
        Args:
            prometheus_data: JSON ответ от Prometheus API
        Returns:
            dict: {node_name: cpu_usage_percent}
        """
        node_cpu = {}

        if 'data' in prometheus_data and 'result' in prometheus_data['data']:
            for result in prometheus_data['data']['result']:
                if 'value' in result and len(result['value']) > 1:
                    try:
                        node_name = result['metric'].get('node_name')
                        cpu_usage = float(result['value'][1])
                        
                        if node_name:
                            # Если уже есть данные для этой ноды, усредняем
                            if node_name in node_cpu:
                                node_cpu[node_name].append(cpu_usage)
                            else:
                                node_cpu[node_name] = [cpu_usage]
                    except (ValueError, TypeError):
                        continue

        # Возвращаем среднее значение для каждой ноды
        return {
            node: sum(values) / len(values)
            for node, values in node_cpu.items()
        }

    def print_cpu_usage_simple(self,cpu_data):
        """Красивое отображение загрузки CPU по серверам"""
        print("=" * 40)
        print("ТЕКУЩАЯ ЗАГРУЗКА CPU ПО СЕРВЕРАМ")
        print("=" * 40)
        
        for i, (server, usage) in enumerate(cpu_data.items(), 1):
            print(f"Сервер {i}: {server}")
            print(f"Загрузка: {usage:.2f}%")
            print("-" * 40)


    # В принципе по CPU должно происходит горизонтальное масшабирование 
    # А по RAM вертикальное масштабирование 
    def run(self) -> None:
        """Запустить одну итерацию проверки и масштабирования"""
        # Получить данные из Prometheus
        prometheus_results = self.get_prometheus_data()
        if not prometheus_results:
            return
        
        # print("Prometheus results:")
        # print(json.dumps(prometheus_results, indent=2))
        
        server_load=self.convert_prometheus_to_list(prometheus_results)
        print(server_load)

        self.print_cpu_usage_simple(server_load)

        # 3. Находим МАКСИМАЛЬНУЮ загрузку среди всех серверов
        max_cpu_usage = max(server_load.values())
        max_server = max(server_load, key=server_load.get)        

        # 4. Выводим информацию о максимальной загрузке
        print(f"Максимальная загрузка: {max_cpu_usage:.2f}% на сервере {max_server}")
        print(f"Порог для scale up: {CPU_PERCENTAGE_UPPER_LIMIT}%")
        print(f"Порог для scale down: {CPU_PERCENTAGE_LOWER_LIMIT}%")
        
        # 5. Получаем текущее количество реплик
        # current_replicas = self.get_current_replicas()
        # print(f"📊 Текущее количество реплик: {current_replicas}")
        
        # 6. Принимаем решение о масштабировании
        if max_cpu_usage > CPU_PERCENTAGE_UPPER_LIMIT:
            print(f"РЕШЕНИЕ: SCALE UP")
            print(f"   Причина: Максимальная загрузка ({max_cpu_usage:.2f}%) превышает порог {CPU_PERCENTAGE_UPPER_LIMIT}%")
            self.scale_up()
        
        elif max_cpu_usage < CPU_PERCENTAGE_LOWER_LIMIT:
            print(f"РЕШЕНИЕ: SCALE DOWN")
            print(f"   Причина: Максимальная загрузка ({max_cpu_usage:.2f}%) ниже порога {CPU_PERCENTAGE_LOWER_LIMIT}%")
            self.scale_down()
        
        else:
            print(f"РЕШЕНИЕ: Без изменений")
            print(f"   Причина: Максимальная загрузка ({max_cpu_usage:.2f}%) в пределах нормы")
        
        # 7. Детальная информация по каждому серверу
        # self.print_detailed_server_analysis(server_load)

def main():
    """Основная функция"""
    try:
        autoscaler = DockerSwarmAutoscaler()
        
        # Запустить первую итерацию
        autoscaler.run()
        
        # Бесконечный цикл, если LOOP установлен в 'yes'
        while LOOP.lower() == 'yes':
            print("\n" + "="*50)
            print(f"Waiting {CHECK_INTERVAL} seconds for the next check")
            print("="*50 + "\n")
            time.sleep(CHECK_INTERVAL)
            autoscaler.run()
            
    except KeyboardInterrupt:
        print("\nПрограмма завершена пользователем")
    except Exception as e:
        print(f"Критическая ошибка: {e}")


if __name__ == "__main__":
    main()