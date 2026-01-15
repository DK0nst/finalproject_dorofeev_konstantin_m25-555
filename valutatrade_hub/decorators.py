import functools
import logging
import time
from datetime import datetime
from typing import Any, Callable, Dict

logger = logging.getLogger(__name__)


def log_action(action_name: str, verbose: bool = False):
    """Декоратор для логирования доменных операций"""
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Собираем данные для логирования
            log_data: Dict[str, Any] = {
                "timestamp": datetime.now().isoformat(),
                "action": action_name,
                "result": "OK"
            }
            
            # Извлекаем полезные параметры из аргументов
            try:
                # Для методов с user_id
                if args and len(args) > 0:
                    if 'user_id' in str(
                        func.__code__.co_varnames[:func.__code__.co_argcount]):
                        user_id_index = list(
                            func.__code__.co_varnames[:func.__code__.co_argcount]
                            ).index('user_id')
                        if user_id_index < len(args):
                            log_data["user_id"] = args[user_id_index]
                
                # Для методов с currency_code
                if 'currency_code' in kwargs:
                    log_data["currency_code"] = kwargs["currency_code"]
                elif args and len(args) > 1 and 'currency_code' in str(
                    func.__code__.co_varnames):
                    currency_index = list(
                        func.__code__.co_varnames[:func.__code__.co_argcount]
                        ).index('currency_code')
                    if currency_index < len(args):
                        log_data["currency_code"] = args[currency_index]
                
                # Для методов с amount
                if 'amount' in kwargs:
                    log_data["amount"] = kwargs["amount"]
                elif args and len(args) > 2 and 'amount' in str(
                    func.__code__.co_varnames):
                    amount_index = list(
                        func.__code__.co_varnames[:func.__code__.co_argcount]
                        ).index('amount')
                    if amount_index < len(args):
                        log_data["amount"] = args[amount_index]
            except Exception:
                pass
            
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                log_data["execution_time"] = f"{execution_time:.3f}s"
                
                # Логирование в структурированном формате
                if verbose:
                    logger.info(f"Подробное логирование {action_name}: {log_data}")
                else:
                    logger.info(f"{action_name} - Успешно: {log_data}")
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                log_data.update({
                    "result": "ERROR",
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "execution_time": f"{execution_time:.3f}s"
                })
                
                logger.error(f"{action_name} - Ошибка: {log_data}")
                raise
        
        return wrapper
    
    return decorator