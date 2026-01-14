import os

# Ключ ExchangeRate-API загружается из переменной окружения
EXCHANGERATE_API_KEY = os.getenv("EXCHANGERATE_API_KEY", "ваш_ключ_здесь")

# URL API
COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"
EXCHANGERATE_API_URL = f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API_KEY}/latest"

# Валюты для отслеживания
BASE_CURRENCY = "USD"
FIAT_CURRENCIES = ["EUR", "GBP", "RUB"]
CRYPTO_CURRENCIES = ["BTC", "ETH", "SOL"]
CRYPTO_ID_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
}

# Пути к файлам
DATA_DIR = "data"
RATES_FILE = f"{DATA_DIR}/rates.json"
HISTORY_FILE = f"{DATA_DIR}/exchange_rates.json"

# Параметры запросов
REQUEST_TIMEOUT = 10