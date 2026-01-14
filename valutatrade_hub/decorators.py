def log_action(action_name):
    """Простой декоратор для логирования действий"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            from valutatrade_hub.logging_config import logger
            logger.info(f"Начало действия: {action_name}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"Действие {action_name} успешно завершено")
                return result
            except Exception as e:
                logger.error(f"Действие {action_name} завершилось ошибкой: {str(e)}")
                raise
        return wrapper
    return decorator