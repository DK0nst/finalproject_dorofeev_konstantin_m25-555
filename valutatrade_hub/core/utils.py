from datetime import datetime

def format_amount(amount: float, currency: str) -> str:
    """Форматирование суммы в зависимости от валюты"""
    if currency in ["BTC", "ETH", "SOL"]:
        return f"{amount:.8f}"
    else:
        return f"{amount:.2f}"

def is_rate_fresh(updated_at: str) -> bool:
    """Проверка свежести курса"""
    try:
        from valutatrade_hub.infra.settings import settings
        update_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        age = (datetime.now() - update_time).total_seconds()
        return age < settings.RATES_TTL
    except:
        return False