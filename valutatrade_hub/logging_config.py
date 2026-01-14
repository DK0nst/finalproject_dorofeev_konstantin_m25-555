import logging

def setup_logging():
    """Минимальная настройка логирования"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('valutatrade.log'),
            logging.StreamHandler()
        ]
    )

# Инициализируем сразу
setup_logging()
logger = logging.getLogger(__name__)