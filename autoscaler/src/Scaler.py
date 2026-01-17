
# Данный скрипт ловит alarm от промитеуса 
# И на основе него увеличивает кол-во реплик 
# Уменьшать кол-во реплик данный скрипт не умеет

from typing import Optional, Tuple
import docker
from docker.errors import DockerException, APIError

class MicroserviceScaler:
    def __init__(self, service_name: str):
        """
        Инициализация масштабатора для указанного сервиса
        
        Args:
            service_name: Имя сервиса в формате 'my-app_my-app'
        """
        self.service_name = service_name
        try:
            self.client = docker.from_env()
        except DockerException as e:
            raise ConnectionError(f"Не удалось подключиться к Docker: {e}")
    
    def get_current_replicas(self) -> Optional[int]:
        """
        Получает текущее количество реплик сервиса
        
        Returns:
            int: Текущее количество реплик или None при ошибке
        """
        try:
            service = self.client.services.get(self.service_name)
            
            # Получаем информацию о режиме сервиса
            service_spec = service.attrs['Spec']['Mode']
            
            if 'Replicated' in service_spec:
                return service_spec['Replicated']['Replicas']
            elif 'Global' in service_spec:
                # Для глобальных сервисов возвращаем количество узлов
                nodes = self.client.nodes.list()
                return len([n for n in nodes if n.attrs['Status']['State'] == 'ready'])
            else:
                print(f"Неизвестный режим сервиса: {service_spec}")
                return None
                
        except APIError as e:
            print(f"Ошибка при получении информации о сервисе: {e}")
            return None
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            return None
    
    def scale_up(self, increment: int = 1) -> Tuple[bool, str]:
        """
        Увеличивает количество реплик сервиса
        
        Args:
            increment: На сколько увеличить количество реплик
            
        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            current_replicas = self.get_current_replicas()
            if current_replicas is None:
                return False, "Не удалось получить текущее количество реплик"
            
            new_replicas = current_replicas + increment
            
            service = self.client.services.get(self.service_name)
            service.update(mode={'Replicated': {'Replicas': new_replicas}})
            
            return True, f"Масштабировано с {current_replicas} до {new_replicas} реплик"
            
        except APIError as e:
            return False, f"Ошибка API Docker: {e}"
        except Exception as e:
            return False, f"Неожиданная ошибка: {e}"
    
    def scale_down(self, decrement: int = 1) -> Tuple[bool, str]:
        """
        Уменьшает количество реплик сервиса
        
        Args:
            decrement: На сколько уменьшить количество реплик
            
        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            current_replicas = self.get_current_replicas()
            if current_replicas is None:
                return False, "Не удалось получить текущее количество реплик"
            
            new_replicas = max(1, current_replicas - decrement)  # Минимум 1 реплика
            
            if new_replicas == current_replicas:
                return True, f"Уже минимальное количество реплик ({current_replicas})"
            
            service = self.client.services.get(self.service_name)
            service.update(mode={'Replicated': {'Replicas': new_replicas}})
            
            return True, f"Масштабировано с {current_replicas} до {new_replicas} реплик"
            
        except APIError as e:
            return False, f"Ошибка API Docker: {e}"
        except Exception as e:
            return False, f"Неожиданная ошибка: {e}"
    
    def scale_to(self, target_replicas: int) -> Tuple[bool, str]:
        """
        Устанавливает точное количество реплик
        
        Args:
            target_replicas: Целевое количество реплик
            
        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            if target_replicas < 1:
                return False, "Количество реплик должно быть не менее 1"
            
            current_replicas = self.get_current_replicas()
            if current_replicas is None:
                return False, "Не удалось получить текущее количество реплик"
            
            service = self.client.services.get(self.service_name)
            service.update(mode={'Replicated': {'Replicas': target_replicas}})
            
            return True, f"Масштабировано с {current_replicas} до {target_replicas} реплик"
            
        except APIError as e:
            return False, f"Ошибка API Docker: {e}"
        except Exception as e:
            return False, f"Неожиданная ошибка: {e}"
    
    def get_service_info(self) -> Optional[dict]:
        """
        Получает подробную информацию о сервисе
        
        Returns:
            dict: Информация о сервисе или None при ошибке
        """
        try:
            service = self.client.services.get(self.service_name)
            return {
                'id': service.id,
                'name': service.name,
                'created_at': service.attrs['CreatedAt'],
                'updated_at': service.attrs['UpdatedAt'],
                'replicas': self.get_current_replicas(),
                'image': service.attrs['Spec']['TaskTemplate']['ContainerSpec']['Image'],
                'ports': service.attrs['Spec']['EndpointSpec'].get('Ports', []),
            }
        except APIError as e:
            print(f"Ошибка при получении информации о сервисе: {e}")
            return None

# Пример использования
if __name__ == "__main__":
    # Инициализация
    scaler = MicroserviceScaler("my-app_my-app")
    
    # Получить текущее количество реплик
    replicas = scaler.get_current_replicas()
    print(f"Текущее количество реплик: {replicas}")
    
    # Увеличить на 2 реплики
    success, message = scaler.scale_up(2)
    print(f"Увеличение: {message}")
    
    # Уменьшить на 1 реплику
    success, message = scaler.scale_down(1)
    print(f"Уменьшение: {message}")
    
    # Установить точное количество
    success, message = scaler.scale_to(3)
    print(f"Установка точного значения: {message}")
    
    # Получить информацию о сервисе
    info = scaler.get_service_info()
    if info:
        print(f"Информация о сервисе: {info}")