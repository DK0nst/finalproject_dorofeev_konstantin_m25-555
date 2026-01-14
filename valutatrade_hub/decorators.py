import functools
from typing import Any, Callable

from .logging_config import logger


def log_action(action_name: str):
    """Простой декоратор для логирования действий"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger.info(f"Начало действия: {action_name}")
            
            try:
                result = func(*args, **kwargs)
                
                # Проверяем, является ли результат кортежем с признаком успеха
                if isinstance(result, tuple) and len(result) >= 2:
                    success, message = result[0], result[1]
                    if success:
                        logger.info(
                            f"Действие {action_name} успешно: {message}")
                    else:
                        logger.warning(
                            f"Действие {action_name} завершилось с ошибкой: {message}")
                elif result is None or (isinstance(result, bool) and not result):
                    logger.warning(f"Действие {action_name} завершилось неудачно")
                else:
                    logger.info(f"Действие {action_name} успешно завершено")
                
                return result
                
            except Exception as e:
                logger.error(
                    f"Действие {action_name} завершилось с исключением: {str(e)}")
                raise
        
        return wrapper
    return decorator