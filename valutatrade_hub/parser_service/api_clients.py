from datetime import datetime

import requests

from . import config


class CoinGeckoClient:
    def __init__(self):
        self.name = "CoinGecko"
    
    def fetch_rates(self):
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
            
        except requests.exceptions.RequestException:
            return {}


class ExchangeRateApiClient:
    def __init__(self):
        self.name = "ExchangeRate-API"
    
    def fetch_rates(self):
        try:
            url = f"{config.EXCHANGERATE_API_URL}/{config.BASE_CURRENCY}"
            response = requests.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            if data.get("result") != "success":
                return {}
            
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
            
        except requests.exceptions.RequestException:
            return {}