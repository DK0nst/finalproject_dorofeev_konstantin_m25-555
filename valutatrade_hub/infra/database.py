import json
from pathlib import Path


class DatabaseManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def read_json(self, filename: str):
        """Чтение JSON файла с обработкой ошибок"""
        filepath = Path("data") / filename
        
        # Если файла нет, возвращаем значение по умолчанию
        if not filepath.exists():
            return [] if filename.endswith(".json") else {}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:  # Если файл пустой
                    return [] if filename.endswith(".json") else {}
                return json.loads(content)
        except (json.JSONDecodeError, ValueError):
            # Если JSON некорректен, возвращаем значение по умолчанию
            print(f"Внимание: Ошибка чтения {filename}. Файл будет перезаписан.")
            return [] if filename.endswith(".json") else {}
    
    def write_json(self, filename: str, data):
        """Запись в JSON файл"""
        filepath = Path("data") / filename
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)

# Глобальный экземпляр
db = DatabaseManager()
