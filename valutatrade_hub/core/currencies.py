from .exceptions import CurrencyNotFoundError

# Словарь валют с минимальной информацией
CURRENCIES = {
    "USD": {"name": "US Dollar", "type": "fiat"},
    "EUR": {"name": "Euro", "type": "fiat"},
    "RUB": {"name": "Russian Ruble", "type": "fiat"},
    "BTC": {"name": "Bitcoin", "type": "crypto"},
    "ETH": {"name": "Ethereum", "type": "crypto"},
    "SOL": {"name": "Solana", "type": "crypto"},
}

def validate_currency_code(code: str) -> bool:
    """Проверка, что валюта поддерживается"""
    return code.upper() in CURRENCIES

def get_currency_info(code: str) -> dict:
    """Получение информации о валюте"""
    code = code.upper()
    if code not in CURRENCIES:
        raise CurrencyNotFoundError(f"Валюта '{code}' не найдена")
    return CURRENCIES[code]