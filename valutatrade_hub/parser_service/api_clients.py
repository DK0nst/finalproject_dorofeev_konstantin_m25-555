from abc import ABC, abstractmethod
from datetime import datetime
import requests

from . import config
from ..core.exceptions import ApiRequestError


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
            url = f"{config.EXCHANGERATE_API_URL}/{config.BASE_CURRENCY}"
            response = requests.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            if data.get("result") != "success":
                raise ApiRequestError(f"API вернуло ошибку: {data.get('error-type', 'unknown')}")
            
            rates = {}
            timestamp = data.get("time_last_update_utc", datetime.now().isoformat())
            base = data.get("base_code", config.BASE_CURRENCY)
            
            for currency in config.FIAT_CURRENCIES:
                if currency in data.get("rates", {}) and currency != base:
                    pair_key = f"{currency}_{base}"
                    rates[pair_key] = {
                        "rate": data["rates"][currency],
                        "updated_at": timestamp,
                        "source": self.name
                    }
            
            return rates
            
        except requests.exceptions.RequestException as e:
            raise ApiRequestError(f"Ошибка при обращении к ExchangeRate-API: {str(e)}")