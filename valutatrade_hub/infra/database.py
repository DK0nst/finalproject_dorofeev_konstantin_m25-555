import json
from pathlib import Path

class DatabaseManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def read_json(self, filename: str):
        """Чтение JSON файла"""
        filepath = Path("data") / filename
        if not filepath.exists():
            return [] if filename.endswith(".json") else {}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def write_json(self, filename: str, data):
        """Запись в JSON файл"""
        filepath = Path("data") / filename
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

# Глобальный экземпляр
db = DatabaseManager()