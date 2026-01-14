class SettingsLoader:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_settings()
        return cls._instance
    
    def _load_settings(self):
        """Загрузка настроек"""
        self.DATA_DIR = "data"
        self.RATES_TTL = 300  # 5 минут
        self.DEFAULT_BASE_CURRENCY = "USD"
        self.API_TIMEOUT = 10
    
    def get(self, key, default=None):
        """Получение настройки"""
        return getattr(self, key, default)

# Глобальный экземпляр
settings = SettingsLoader()