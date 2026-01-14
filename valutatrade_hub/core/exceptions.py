class ValutaTradeException(Exception):
    """Базовое исключение для ValutaTrade"""
    pass

class InsufficientFundsError(ValutaTradeException):
    """Недостаточно средств"""
    pass

class CurrencyNotFoundError(ValutaTradeException):
    """Валюта не найдена"""
    pass

class ApiRequestError(ValutaTradeException):
    """Ошибка API"""
    pass