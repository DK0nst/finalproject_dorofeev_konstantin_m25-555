from abc import ABC, abstractmethod

from .exceptions import CurrencyNotFoundError


class Currency(ABC):
    """Абстрактный базовый класс для валют"""
    
    def __init__(self, name: str, code: str):
        if not name or not isinstance(name, str):
            raise ValueError("Название валюты не может быть пустым")
        if not (2 <= len(code) <= 5) or not code.isupper() or ' ' in code:
            raise ValueError(
                "Код валюты должен быть в верхнем регистре, 2-5 символов, без пробелов")
        self._name = name
        self._code = code
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def code(self) -> str:
        return self._code
    
    @abstractmethod
    def get_display_info(self) -> str:
        """Строковое представление для UI/логов"""
        pass


class FiatCurrency(Currency):
    """Фиатная валюта"""
    
    def __init__(self, name: str, code: str, issuing_country: str):
        super().__init__(name, code)
        self._issuing_country = issuing_country
    
    @property
    def issuing_country(self) -> str:
        return self._issuing_country
    
    def get_display_info(self) -> str:
        message = f"[FIAT] {self._code} --- {self._name}" 
        message = message + f" (Issuing: {self._issuing_country})"
        return message


class CryptoCurrency(Currency):
    """Криптовалюта"""
    
    def __init__(self, name: str, code: str, algorithm: str, market_cap: float = 0.0):
        super().__init__(name, code)
        self._algorithm = algorithm
        self._market_cap = market_cap
    
    @property
    def algorithm(self) -> str:
        return self._algorithm
    
    @property
    def market_cap(self) -> float:
        return self._market_cap
    
    def get_display_info(self) -> str:
        message = f"[CRYPTO] {self._code} --- {self._name}" 
        message = message + f" (Algo: {self._algorithm}, MCAP: {self._market_cap:.2e})"
        return message


# Реестр валют
_currency_registry = {}


def register_currency(currency: Currency):
    """Регистрация валюты в реестре"""
    _currency_registry[currency.code] = currency


def get_currency(code: str) -> Currency:
    """Фабричный метод для получения валюты по коду"""
    code = code.upper()
    if code not in _currency_registry:
        raise CurrencyNotFoundError(f"Неизвестная валюта '{code}'")
    return _currency_registry[code]


def validate_currency_code(code: str) -> bool:
    """Проверка, что валюта поддерживается"""
    try:
        get_currency(code)
        return True
    except CurrencyNotFoundError:
        return False


def get_all_currencies():
    """Получение всех зарегистрированных валют"""
    return _currency_registry.copy()


# Инициализация реестра
register_currency(FiatCurrency("US Dollar", "USD", "United States"))
register_currency(FiatCurrency("Euro", "EUR", "Eurozone"))
register_currency(FiatCurrency("Russian Ruble", "RUB", "Russia"))
register_currency(CryptoCurrency("Bitcoin", "BTC", "SHA-256", 1.12e12))
register_currency(CryptoCurrency("Ethereum", "ETH", "Ethash", 4.5e11))
register_currency(CryptoCurrency("Solana", "SOL", "Proof of History", 3.4e10))