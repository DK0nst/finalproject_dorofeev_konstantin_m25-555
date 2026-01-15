from abc import ABC, abstractmethod
from datetime import datetime

import requests

from ..core.exceptions import ApiRequestError
from . import config


class BaseApiClient(ABC):
    """Абстрактный базовый класс для API клиентов"""
    
    @abstractmethod
    def fetch_rates(self) -> dict:
        """Получение курсов валют"""
        pass


class CoinGeckoClient(BaseApiClient):
    def __init__(self):
        self.name = "CoinGecko"
    
    def fetch_rates(self) -> dict:
        try:
            ids = ",".join(config.CRYPTO_ID_MAP.values())
            url = f"{config.COINGECKO_URL}?ids={ids}&vs_currencies=usd"
            response = requests.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            rates = {}
            timestamp = datetime.now().isoformat()
            
            for code, coin_id in config.CRYPTO_ID_MAP.items():
                if coin_id in data and "usd" in data[coin_id]:
                    pair_key = f"{code}_{config.BASE_CURRENCY}"
                    rates[pair_key] = {
                        "rate": data[coin_id]["usd"],
                        "updated_at": timestamp,
                        "source": self.name
                    }
            
            return rates
            
        except requests.exceptions.RequestException as e:
            raise ApiRequestError(f"Ошибка при обращении к CoinGecko API: {str(e)}")


class ExchangeRateApiClient(BaseApiClient):
    def __init__(self):
        self.name = "ExchangeRate-API"
    
    def fetch_rates(self) -> dict:
        try:
            # Формируем URL
            url = f"{config.EXCHANGERATE_API_URL}/{config.BASE_CURRENCY}"
            
            # Отладочная информация
            print(f"DEBUG: Запрос к ExchangeRate-API: {url}")
            
            response = requests.get(url, timeout=config.REQUEST_TIMEOUT)
            
            print(f"DEBUG: Статус код: {response.status_code}")
            
            response.raise_for_status()
            data = response.json()
            
            print(f"DEBUG: Результат API: {data.get('result', 'unknown')}")
            
            if data.get("result") != "success":
                error_type = data.get("error-type", "unknown")
                raise ApiRequestError(f"ExchangeRate-API вернуло ошибку: {error_type}")
            
            rates = {}
            timestamp = data.get("time_last_update_utc", datetime.now().isoformat())
            base = data.get("base_code", config.BASE_CURRENCY)
            
            print(f"DEBUG: Базовая валюта: {base}")
            print(f"DEBUG: Ключи в ответе: {list(data.keys())}")
            
            # ВАЖНО: API возвращает курсы в поле "conversion_rates", а не "rates"!
            conversion_rates = data.get("conversion_rates", {})
            print(f"DEBUG: Всего валют в conversion_rates: {len(conversion_rates)}")
            
            # Получаем курсы для нужных нам валют
            for currency in config.FIAT_CURRENCIES:
                if currency in conversion_rates and currency != base:
                    pair_key = f"{currency}_{base}"
                    rates[pair_key] = {
                        "rate": conversion_rates[currency],
                        "updated_at": timestamp,
                        "source": self.name
                    }
                    print(f"DEBUG: Найден курс {pair_key} = {conversion_rates[currency]}")
            
            print(f"DEBUG: ExchangeRate-API вернул {len(rates)} курсов")
            return rates
            
        except requests.exceptions.RequestException as e:
            print(f"DEBUG: Исключение при запросе: {str(e)}")
            raise ApiRequestError(f"Ошибка при обращении к ExchangeRate-API: {str(e)}")