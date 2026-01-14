import time
from .updater import RatesUpdater

class UpdateScheduler:
    def __init__(self, interval_minutes: int = 5):
        self.interval = interval_minutes * 60
        self.updater = RatesUpdater()
        self.running = False
    
    def start(self):
        """Запуск планировщика"""
        self.running = True
        print(f"Планировщик запущен, интервал: {self.interval//60} минут")
        
        while self.running:
            self.updater.run_update()
            time.sleep(self.interval)
    
    def stop(self):
        """Остановка планировщика"""
        self.running = False
        print("Планировщик остановлен")