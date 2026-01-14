import json
from datetime import datetime
from pathlib import Path

from . import config
from .api_clients import CoinGeckoClient, ExchangeRateApiClient


class RatesUpdater:
    def __init__(self):
        self.coingecko_client = CoinGeckoClient()
        self.exchangerate_client = ExchangeRateApiClient()
    
    def run_update(self, source: str = None):
        all_rates = {}
        
        # Обновление от CoinGecko
        if not source or source == "coingecko":
            rates = self.coingecko_client.fetch_rates()
            if rates:
                all_rates.update(rates)
                print(f"CoinGecko: получено {len(rates)} курсов")
        
        # Обновление от ExchangeRate-API
        if not source or source == "exchangerate":
            rates = self.exchangerate_client.fetch_rates()
            if rates:
                all_rates.update(rates)
                print(f"ExchangeRate-API: получено {len(rates)} курсов")
        
        # Сохранение в rates.json
        if all_rates:
            result = {
                "pairs": all_rates,
                "last_refresh": datetime.now().isoformat()
            }
            
            filepath = Path(config.RATES_FILE)
            filepath.parent.mkdir(exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, default=str)
            
            print(f"Обновлено {len(all_rates)} курсов")
            return True
        
        print("Не удалось получить курсы")
        return False