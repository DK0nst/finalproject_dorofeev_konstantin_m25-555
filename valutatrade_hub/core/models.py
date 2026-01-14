import hashlib
import os
from datetime import datetime
from typing import Dict, Optional

from .currencies import validate_currency_code
from .exceptions import InsufficientFundsError


class User:
    def __init__(self, user_id: int, username: str, password: str, salt: str = None):
        self._user_id = user_id
        self._username = username
        self._salt = salt or os.urandom(16).hex()
        self._hashed_password = self._hash_password(password, self._salt)
        self._registration_date = datetime.now()
    
    def _hash_password(self, password: str, salt: str) -> str:
        return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
    
    def get_user_info(self) -> Dict:
        return {
            "user_id": self._user_id,
            "username": self._username,
            "registration_date": self._registration_date.isoformat()
        }
    
    def change_password(self, new_password: str):
        if len(new_password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов")
        self._hashed_password = self._hash_password(new_password, self._salt)
    
    def verify_password(self, password: str) -> bool:
        return self._hashed_password == self._hash_password(password, self._salt)
    
    def to_dict(self) -> Dict:
        return {
            "user_id": self._user_id,
            "username": self._username,
            "hashed_password": self._hashed_password,
            "salt": self._salt,
            "registration_date": self._registration_date.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            user_id=data["user_id"],
            username=data["username"],
            password="",
            salt=data["salt"]
        )


class Wallet:
    def __init__(self, currency_code: str, balance: float = 0.0):
        if not validate_currency_code(currency_code):
            raise ValueError(f"Неизвестная валюта: {currency_code}")
        
        self.currency_code = currency_code.upper()
        self._balance = float(balance)
        if self._balance < 0:
            raise ValueError("Баланс не может быть отрицательным")
    
    @property
    def balance(self) -> float:
        return self._balance
    
    @balance.setter
    def balance(self, value: float):
        value = float(value)
        if value < 0:
            raise ValueError("Баланс не может быть отрицательным")
        self._balance = value
    
    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")
        self.balance += amount
    
    def withdraw(self, amount: float):
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной")
        if amount > self._balance:
            raise InsufficientFundsError(
                f"Недостаточно средств. Доступно: {self._balance} {self.currency_code}"
            )
        self.balance -= amount
    
    def to_dict(self) -> Dict:
        return {
            "currency_code": self.currency_code,
            "balance": self._balance
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            currency_code=data["currency_code"],
            balance=data["balance"]
        )


class Portfolio:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.wallets = {}
    
    def add_currency(self, currency_code: str):
        currency_code = currency_code.upper()
        if not validate_currency_code(currency_code):
            raise ValueError(f"Неизвестная валюта: {currency_code}")
        
        if currency_code not in self.wallets:
            self.wallets[currency_code] = Wallet(currency_code)
    
    def get_wallet(self, currency_code: str) -> Optional[Wallet]:
        return self.wallets.get(currency_code.upper())
    
    def get_total_value(self, base_currency: str = 'USD') -> float:
        from ..infra.database import db
        from .utils import is_rate_fresh
        
        rates = db.read_json("rates.json")
        pairs = rates.get("pairs", {})
        
        total = 0.0
        for wallet in self.wallets.values():
            if wallet.currency_code == base_currency:
                total += wallet.balance
            else:
                pair_key = f"{wallet.currency_code}_{base_currency}"
                if pair_key in pairs:
                    rate_info = pairs[pair_key]
                    if is_rate_fresh(rate_info.get("updated_at", "")):
                        total += wallet.balance * rate_info["rate"]
        
        return total
    
    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "wallets": {
                code: wallet.to_dict() 
                for code, wallet in self.wallets.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        portfolio = cls(data["user_id"])
        for code, wallet_data in data["wallets"].items():
            portfolio.wallets[code] = Wallet.from_dict(wallet_data)
        return portfolio