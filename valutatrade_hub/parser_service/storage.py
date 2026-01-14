import json
from datetime import datetime
from pathlib import Path


class DataStorage:
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
    
    def save_rates(self, rates_data: dict):
        """Сохранение текущих курсов в rates.json"""
        filepath = self.data_dir / "rates.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(rates_data, f, indent=2, default=str)
    
    def save_historical(self, historical_data: list):
        """Сохранение исторических данных"""
        filepath = self.data_dir / "exchange_rates.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(historical_data, f, indent=2, default=str)
    
    def load_historical(self) -> list:
        """Загрузка исторических данных"""
        filepath = self.data_dir / "exchange_rates.json"
        if not filepath.exists():
            return []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)