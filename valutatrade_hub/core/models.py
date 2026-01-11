import hashlib
import random
import string
from datetime import datetime
from typing import Dict, Optional

"""
Общие заменчания

Пользователи
!!! Подумать, м.б. переделать.
Дата возвращается в ИСО формате.
Вероятно verify_password стоит проверять в change_password
Добавлена генерация соли generate_salt

Кошелек
Возвращаем словарь в get_balance_info
{
            "currency_code": self.currency_code,
            "balance": self.balance
        }

"""

"""
Класс User (пользователь системы)  

Атрибуты:
+ _user_id: int — уникальный идентификатор пользователя.
+ _username: str — имя пользователя.
+ _hashed_password: str — пароль в зашифрованном виде.
+ _salt: str — уникальная соль для пользователя.
+ _registration_date: datetime — дата регистрации пользователя.

Методы класса:
+ get_user_info() — выводит информацию о пользователе (без пароля).
+ change_password(new_password: str) — изменяет пароль пользователя, с хешированием нового пароля.
+ verify_password(password: str) — проверяет введённый пароль на совпадение.

Задачи:
+ Реализовать класс User с конструктором (__init__), принимающим все параметры в models.py.
+ Сделать все атрибуты приватными (через _имя).
+ Реализовать методы get_user_info() и change_password().
+ В методе change_password делайте односторонний псевдо-хеш (например, hashlib.sha256(password + salt)), соль храните рядом.
+ Для каждого атрибута реализовать геттер 
+    и, где необходимо, сеттер с проверками (сделаны на каждый атрибут):
+ Имя не может быть пустым.
+ Пароль должен быть не короче 4 символов.
"""

class User:
    """Пользователь системы."""
    
    def __init__(self, user_id: int, username: str, hashed_password: str, 
                 salt: str, registration_date: datetime):

        """Инициализация с проверкой через сеттеры"""

        # Внимание! Тут присваивание происходит через методы с сеттерами.
        # Там проверка происходит и присваивание в приватные атрибуты
        self.user_id = user_id
        self.username = username
        self.hashed_password = hashed_password
        self.salt = salt
        self.registration_date = registration_date
    
    # Геттеры
    @property
    def user_id(self) -> int:
        return self._user_id
    
    @property
    def username(self) -> str:
        return self._username
    
    @property
    def hashed_password(self) -> str:
        return self._hashed_password
    
    @property
    def salt(self) -> str:
        return self._salt
    
    @property
    def registration_date(self) -> datetime:
        return self._registration_date
    
    # Сеттеры с проверками
    @user_id.setter
    def user_id(self, value: int):
        if not isinstance(value, int):
            raise TypeError("user_id должен быть целым числом")
        self._user_id = value
    
    @username.setter
    def username(self, value: str):
        if not isinstance(value, str):
            raise TypeError("username должен быть строкой")
        if not value.strip():
            raise ValueError("Имя не может быть пустым")
        self._username = value
    
    @hashed_password.setter
    def hashed_password(self, value: str):
        if not isinstance(value, str):
            raise TypeError("hashed_password должен быть строкой")
        
        # SHA256 хеш всегда 64 символа в hex
        if len(value) != 64:
            raise ValueError("Хешированный пароль должен быть 64 символа (SHA256)")
        self._hashed_password = value
    
    @salt.setter
    def salt(self, value: str):
        if not isinstance(value, str):
            raise TypeError("salt должен быть строкой")
        self._salt = value
    
    @registration_date.setter
    def registration_date(self, value: datetime):
        if not isinstance(value, datetime):
            raise TypeError("registration_date должен быть datetime")
        self._registration_date = value
    
    # Методы класса
    def get_user_info(self) -> dict:
        """Выводит информацию о пользователе (без пароля)."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "salt": self.salt,
            "registration_date": self.registration_date.isoformat()
        }
    
    def change_password(self, new_password: str):
        """Изменяет пароль пользователя с хешированием."""
        if len(new_password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов")
        
        # Односторонний псевдо-хеш
        salted_password = new_password + self.salt
        self.hashed_password = hashlib.sha256(salted_password.encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """Проверяет введённый пароль на совпадение."""
        salted_password = password + self.salt
        return self.hashed_password == hashlib.sha256(salted_password.encode()).hexdigest()
    
    # Статические методы для создания пользователя
    @staticmethod
    def generate_salt(length: int = 8) -> str:
        """Генерирует случайную соль."""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choice(chars) for _ in range(length))


"""
Класс Wallet (кошелёк пользователя для одной конкретной валюты) 

Атрибуты:
+ currency_code: str — код валюты (например, "USD", "BTC").
+ _balance: float — баланс в данной валюте (по умолчанию 0.0).

Методы класса:
+ deposit(amount: float) — пополнение баланса.
+ withdraw(amount: float) — снятие средств (если баланс позволяет).
+ get_balance_info() — вывод информации о текущем балансе.  

Задачи:
+ Реализовать класс Wallet с конструктором (__init__), принимающим все параметры в models.py.
+ Реализовать методы deposit() и get_balance_info().
+ Создать свойство balance с:
+ Геттером (@property) — возвращает текущее значение.
+ Сеттером (@balance.setter) — запрещает отрицательные значения и некорректные типы данных.
+ В методе withdraw проверять, что сумма снятия не превышает баланс.
+ Добавить проверку, что amount — положительное число.
"""


class Wallet:
    """Класс кошелька для одной валюты."""
    
    def __init__(self, currency_code: str, balance: float = 0.0):
        """
        Инициализация кошелька.
        """

        # Используем сеттер для проверки
        self.currency_code = currency_code
        self.balance = balance  
    
    # Свойство balance с геттером и сеттером
    @property
    def balance(self) -> float:
        """Возвращает текущий баланс."""
        return self._balance
    
    @balance.setter
    def balance(self, value: float) -> None:
        """Устанавливает баланс с проверками."""
        if not isinstance(value, (int, float)):
            raise TypeError("Баланс должен быть числом")
        if value < 0:
            raise ValueError("Баланс не может быть отрицательным")
        self._balance = float(value)
    
    @property
    def currency_code(self) -> str:
        """Возвращает код валюты."""
        return self._currency_code
    
    @currency_code.setter
    def currency_code(self, value: str) -> None:
        """Устанавливает код валюты с проверками."""
        if not isinstance(value, str):
            raise TypeError("Код валюты должен быть строкой")
        if not value.strip():
            raise ValueError("Код валюты не может быть пустым")
        self._currency_code = value.strip().upper()
    
    def deposit(self, amount: float) -> None:
        """
        Пополнение баланса.

        amount: сумма для пополнения
        amount д.б.. больше 0, иначе возвращаем ошибку
        """
        if not isinstance(amount, (int, float)):
            raise TypeError("Сумма должна быть числом")
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")
        
        self.balance += amount
    
    def withdraw(self, amount: float) -> None:
        """
        Снятие средств с баланса.

        amount: сумма для снятия
        amount д.б. больше депозита, иначе возвращаем ошибку
        """
        if not isinstance(amount, (int, float)):
            raise TypeError("Сумма должна быть числом")
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной")
        if amount > self.balance:
            raise ValueError(f"Недостаточно средств. Доступно: {self.balance}")
        
        self.balance -= amount
    
    def get_balance_info(self) -> dict:
        """
        Возвращает информацию о текущем балансе.
        Словарь с информацией о кошельке в удобном для сохранения в json формате
        """
        return {
            "currency_code": self.currency_code,
            "balance": self.balance
        }
    

"""
Класс Portfolio (управление всеми кошельками одного пользователя)  
Атрибуты:
+ _user_id: int — уникальный идентификатор пользователя.
+ _wallets: dict[str, Wallet] — словарь кошельков, где ключ — код валюты, значение — объект Wallet.

Методы класса:
+ add_currency(currency_code: str) — добавляет новый кошелёк в портфель (если его ещё нет).
+ get_total_value(base_currency='USD') — возвращает общую стоимость всех валют пользователя в указанной базовой валюте (по курсам, полученным из API или фиктивным данным).
+ get_wallet(currency_code) — возвращает объект Wallet по коду валюты.

Задачи:
+ Реализовать класс Portfolio с конструктором (__init__), принимающим все параметры в models.py.
+ Реализовать метод add_currency, который создаёт новый объект Wallet и добавляет его в словарь.
+ В методе add_currency проверять, что код валюты уникален.
+ Реализовать метод get_total_value, который конвертирует балансы всех валют в base_currency (для упрощения можно задать фиксированные курсы в словаре exchange_rates).
Добавить свойства:
+ user — геттер, который возвращает объект пользователя (без возможности перезаписи).
+ wallets — геттер, который возвращает копию словаря кошельков.

Логика:
+ При покупке валюты сумма списывается с USD-кошелька.
+ При продаже — сумма начисляется на USD-кошелёк.
"""

class Portfolio:
    """Управление всеми кошельками одного пользователя"""
    
    # Фиксированные курсы для конвертации
    exchange_rates = {
        "USD_USD": 1.0,
        "EUR_USD": 1.0786,
        "BTC_USD": 59337.21,
        "RUB_USD": 0.01016,
        "ETH_USD": 3720.00
    }
    
    def __init__(self, user_id: int, wallets: Dict[str, 'Wallet'] = None):
        """
        Инициализация портфеля.
            user_id: Уникальный идентификатор пользователя
            wallets: Словарь кошельков (ключ - код валюты, значение - Wallet)
        """
        self.user_id = user_id
        self._wallets = wallets if wallets is not None else {}
    
    @property
    def user_id(self) -> int:
        """Возвращает ID пользователя."""
        return self._user_id
    
    @user_id.setter
    def user_id(self, value: int) -> None:
        """Устанавливает ID пользователя с проверкой."""
        if not isinstance(value, int):
            raise TypeError("user_id должен быть целым числом")
        if value <= 0:
            raise ValueError("user_id должен быть положительным числом")
        self._user_id = value
    
    @property
    def wallets(self) -> Dict[str, 'Wallet']:
        """Возвращает копию словаря кошельков."""
        return self._wallets.copy()
    
    def add_currency(self, currency_code: str) -> None:
        """
        Добавляет новый кошелёк в портфель (если его ещё нет).
        currency_code: Код валюты для добавления
        Ошибка: если валюта уже есть в портфеле
        """
        if currency_code in self._wallets:
            raise ValueError(f"Валюта {currency_code} уже есть в портфеле")
        
        # Создаём новый кошелёк с балансом 0.0
        new_wallet = Wallet(currency_code=currency_code, balance=0.0)
        self._wallets[currency_code] = new_wallet
    
    def get_wallet(self, currency_code: str) -> Optional['Wallet']:
        """
        Возвращает объект Wallet по коду валюты.
        Аргументы: currency_code: Код валюты
        Возвращает: объект Wallet или None, если кошелёк не найден
        """
        return self._wallets.get(currency_code)
    
    def get_total_value(self, base_currency: str = 'USD') -> float:
        """
        Возвращает общую стоимость всех валют в указанной базовой валюте.
        base_currency: Базовая валюта для конвертации (по умолчанию USD)
        Общая стоимость в базовой валюте
        Ошибка: Если курс для какой-либо валюты не найден
        """
        total_value = 0.0
        
        for currency_code, wallet in self._wallets.items():
            if currency_code == base_currency:
                # Если валюта совпадает с базовой, просто добавляем баланс
                total_value += wallet.balance
            else:
                # Пытаемся найти курс для конвертации
                rate_key = f"{currency_code}_{base_currency}"
                if rate_key in self.exchange_rates:
                    rate = self.exchange_rates[rate_key]
                    total_value += wallet.balance * rate
                else:
                    raise ValueError(
                        f"Не удалось найти курс для конвертации "
                        f"{currency_code} -> {base_currency}"
                    )
        
        return total_value