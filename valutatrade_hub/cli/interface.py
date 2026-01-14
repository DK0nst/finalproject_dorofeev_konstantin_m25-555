"""
Командный интерфейс (CLI)
"""

import argparse
import sys
from ..core.usecases import register_user


def main():
    """Основная функция CLI (только команда register)."""
    parser = argparse.ArgumentParser(
        description="Регистрация нового пользователя",
        prog="valutatrade"
    )
    
    # Создаем подпарсер для команды register
    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")
    register_parser = subparsers.add_parser("register", help="Регистрация нового пользователя")
    
    # Аргументы для команды register
    register_parser.add_argument("--username", type=str, required=True, help="Имя пользователя")
    register_parser.add_argument("--password", type=str, required=True, help="Пароль")
    
    args = parser.parse_args()
    
    # Если не указана команда, показываем справку
    if not args.command:
        parser.print_help()
        return 1
    
    # Обрабатываем команду register
    if args.command == "register":
        result = register_user(args.username, args.password)
        print(result)
        # Возвращаем 0 если успешно, 1 если ошибка
        return 0 if "зарегистрирован" in result else 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())