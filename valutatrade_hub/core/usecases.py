from typing import Optional, Tuple
from datetime import datetime

from .models import User, Portfolio, Wallet
from .exceptions import (
    InsufficientFundsError, CurrencyNotFoundError, 
    ApiRequestError, ValutaTradeException
)
from .currencies import validate_currency_code
from ..decorators import log_action
from ..infra.database import db


def get_next_user_id() -> int:
    """Генерация следующего ID пользователя"""
    users = db.read_json("users.json")
    if not users:
        return 1
    return max(user["user_id"] for user in users) + 1


class UserManager:
    @staticmethod
    @log_action("REGISTER")
    def register_user(username: str, password: str) -> Tuple[bool, str, Optional[int]]:
        users = db.read_json("users.json")
        
        if any(user["username"] == username for user in users):
            return False, f"Имя пользователя '{username}' уже занято", None
        
        if len(password) < 4:
            return False, "Пароль должен быть не короче 4 символов", None
        
        user_id = get_next_user_id()
        user = User(user_id, username, password)
        
        users.append(user.to_dict())
        db.write_json("users.json", users)
        
        portfolios = db.read_json("portfolios.json")
        portfolio = Portfolio(user_id)
        portfolios.append(portfolio.to_dict())
        db.write_json("portfolios.json", portfolios)
        
        return True, f"Пользователь '{username}' зарегистрирован (id={user_id})", user_id
    
    @staticmethod
    @log_action("LOGIN")
    def login_user(username: str, password: str) -> Tuple[bool, str, Optional[User]]:
        users = db.read_json("users.json")
        
        for user_data in users:
            if user_data["username"] == username:
                user = User.from_dict(user_data)
                if user.verify_password(password):
                    return True, f"Вы вошли как '{username}'", user
        
        return False, "Неверное имя пользователя или пароль", None


class PortfolioManager:
    @staticmethod
    def get_user_portfolio(user_id: int) -> Optional[Portfolio]:
        portfolios = db.read_json("portfolios.json")
        
        for portfolio_data in portfolios:
            if portfolio_data["user_id"] == user_id:
                return Portfolio.from_dict(portfolio_data)
        
        return None
    
    @staticmethod
    def update_portfolio(portfolio: Portfolio):
        portfolios = db.read_json("portfolios.json")
        
        for i, portfolio_data in enumerate(portfolios):
            if portfolio_data["user_id"] == portfolio.user_id:
                portfolios[i] = portfolio.to_dict()
                break
        else:
            portfolios.append(portfolio.to_dict())
        
        db.write_json("portfolios.json", portfolios)
    
    @staticmethod
    @log_action("BUY")
    def buy_currency(user_id: int, currency_code: str, amount: float) -> Tuple[bool, str]:
        if amount <= 0:
            return False, "Количество должно быть положительным числом"
        
        if not validate_currency_code(currency_code):
            return False, f"Неизвестная валюта: {currency_code}"
        
        portfolio = PortfolioManager.get_user_portfolio(user_id)
        if not portfolio:
            return False, "Портфель не найден"
        
        # Получаем курс
        rates = db.read_json("rates.json")
        pairs = rates.get("pairs", {})
        pair_key = f"{currency_code}_USD"
        
        if pair_key not in pairs:
            return False, f"Не удалось получить курс для {currency_code}"
        
        rate = pairs[pair_key]["rate"]
        cost_usd = amount * rate
        
        # Проверяем баланс USD
        usd_wallet = portfolio.get_wallet("USD")
        if not usd_wallet or usd_wallet.balance < cost_usd:
            return False, f"Недостаточно средств. Нужно: {cost_usd:.2f} USD"
        
        try:
            # Выполняем покупку
            usd_wallet.withdraw(cost_usd)
            
            target_wallet = portfolio.get_wallet(currency_code)
            if not target_wallet:
                portfolio.add_currency(currency_code)
                target_wallet = portfolio.get_wallet(currency_code)
            
            target_wallet.deposit(amount)
            PortfolioManager.update_portfolio(portfolio)
            
            return True, f"Куплено {amount:.4f} {currency_code} за {cost_usd:.2f} USD"
            
        except ValutaTradeException as e:
            return False, str(e)
    
    @staticmethod
    @log_action("SELL")
    def sell_currency(user_id: int, currency_code: str, amount: float) -> Tuple[bool, str]:
        if amount <= 0:
            return False, "Количество должно быть положительным числом"
        
        if not validate_currency_code(currency_code):
            return False, f"Неизвестная валюта: {currency_code}"
        
        portfolio = PortfolioManager.get_user_portfolio(user_id)
        if not portfolio:
            return False, "Портфель не найден"
        
        target_wallet = portfolio.get_wallet(currency_code)
        if not target_wallet:
            return False, f"У вас нет валюты '{currency_code}'"
        
        try:
            # Проверяем баланс
            if target_wallet.balance < amount:
                return False, f"Недостаточно {currency_code}. Доступно: {target_wallet.balance:.4f}"
            
            # Получаем курс
            rates = db.read_json("rates.json")
            pairs = rates.get("pairs", {})
            pair_key = f"{currency_code}_USD"
            
            if pair_key not in pairs:
                return False, f"Не удалось получить курс для {currency_code}"
            
            rate = pairs[pair_key]["rate"]
            revenue_usd = amount * rate
            
            # Выполняем продажу
            target_wallet.withdraw(amount)
            
            usd_wallet = portfolio.get_wallet("USD")
            if not usd_wallet:
                portfolio.add_currency("USD")
                usd_wallet = portfolio.get_wallet("USD")
            
            usd_wallet.deposit(revenue_usd)
            PortfolioManager.update_portfolio(portfolio)
            
            return True, f"Продано {amount:.4f} {currency_code} за {revenue_usd:.2f} USD"
            
        except ValutaTradeException as e:
            return False, str(e)


class RateManager:
    @staticmethod
    @log_action("GET_RATE")
    def get_rate(from_currency: str, to_currency: str) -> Tuple[bool, str, Optional[float]]:
        if not from_currency or not to_currency:
            return False, "Коды валют не могут быть пустыми", None
        
        if not validate_currency_code(from_currency) or not validate_currency_code(to_currency):
            return False, f"Неизвестная валюта", None
        
        rates = db.read_json("rates.json")
        pairs = rates.get("pairs", {})
        
        # Прямой курс
        pair_key = f"{from_currency}_{to_currency}"
        if pair_key in pairs:
            rate_info = pairs[pair_key]
            return True, f"Курс {from_currency}→{to_currency}: {rate_info['rate']:.6f}", rate_info['rate']
        
        # Обратный курс
        reverse_key = f"{to_currency}_{from_currency}"
        if reverse_key in pairs:
            rate = 1 / pairs[reverse_key]["rate"]
            return True, f"Курс {from_currency}→{to_currency}: {rate:.6f}", rate
        
        return False, f"Курс {from_currency}→{to_currency} недоступен", None