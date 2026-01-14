"""
Бизнес-логика приложения
"""

import json
import hashlib
import random
import string
from datetime import datetime
from pathlib import Path


def _generate_salt(length: int = 8) -> str:
    """Генерирует случайную соль для пароля."""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))


def _hash_password(password: str, salt: str) -> str:
    """Хеширует пароль с солью."""
    salted_password = password + salt
    return hashlib.sha256(salted_password.encode()).hexdigest()


def _load_users():
    """Загружает пользователей из users.json."""
    users_file = Path("data/users.json")
    if not users_file.exists():
        return []
    
    with open(users_file, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _save_users(users):
    """Сохраняет пользователей в users.json."""
    users_file = Path("data/users.json")
    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def _load_portfolios():
    """Загружает портфели из portfolios.json."""
    portfolios_file = Path("data/portfolios.json")
    if not portfolios_file.exists():
        return []
    
    with open(portfolios_file, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _save_portfolios(portfolios):
    """Сохраняет портфели в portfolios.json."""
    portfolios_file = Path("data/portfolios.json")
    with open(portfolios_file, 'w', encoding='utf-8') as f:
        json.dump(portfolios, f, ensure_ascii=False, indent=2)


def register_user(username: str, password: str) -> str:
    """
    Регистрирует нового пользователя.
    
    Шаги:
    1. Проверить уникальность username в users.json
    2. Сгенерировать user_id (автоинкремент)
    3. Захешировать пароль (hashlib.sha256(password + salt))
    4. Сохранить пользователя в users.json
    5. Создать пустой портфель (portfolios.json: user_id + пустой словарь кошельков)
    6. Вернуть сообщение об успехе
    """
    # 1. Проверить уникальность username
    users = _load_users()
    for user in users:
        if user.get("username") == username:
            return f"Имя пользователя '{username}' уже занято"
    
    # 2. Проверка пароля
    if len(password) < 4:
        return "Пароль должен быть не короче 4 символов"
    
    # 3. Сгенерировать user_id
    if users:
        user_id = max(user.get("user_id", 0) for user in users) + 1
    else:
        user_id = 1
    
    # 4. Захешировать пароль
    salt = _generate_salt()
    hashed_password = _hash_password(password, salt)
    registration_date = datetime.now().isoformat()
    
    # 5. Сохранить пользователя
    new_user = {
        "user_id": user_id,
        "username": username,
        "hashed_password": hashed_password,
        "salt": salt,
        "registration_date": registration_date
    }
    users.append(new_user)
    _save_users(users)
    
    # 6. Создать пустой портфель
    portfolios = _load_portfolios()
    new_portfolio = {
        "user_id": user_id,
        "wallets": {}
    }
    portfolios.append(new_portfolio)
    _save_portfolios(portfolios)
    
    # 7. Вернуть сообщение об успехе
    return f"Пользователь '{username}' зарегистрирован (id={user_id}). Войдите: login --username {username} --password ****"