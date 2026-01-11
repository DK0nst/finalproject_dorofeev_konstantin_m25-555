import hashlib
import random
import string
from datetime import datetime

"""
Общие заменчания

Пользователи
!!! Подумать, м.б. переделать.
Дата возвращается в ИСО формате.
Вероятно verify_password стоит проверять в change_password
Добавлена генерация соли generate_salt

Кошелек

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