import argparse
import sys
from ..core.usecases import UserManager, PortfolioManager, RateManager
from ..parser_service.updater import RatesUpdater
from ..parser_service.storage import DataStorage
from ..parser_service.scheduler import UpdateScheduler
from ..core.currencies import CURRENCIES
from ..core.exceptions import ValutaTradeException

class Session:
    current_user = None
    
    @classmethod
    def login(cls, user):
        cls.current_user = user
    
    @classmethod
    def logout(cls):
        cls.current_user = None
    
    @classmethod
    def is_logged_in(cls):
        return cls.current_user is not None


def register_command(args):
    success, message, _ = UserManager.register_user(args.username, args.password)
    print(message)
    return success


def login_command(args):
    success, message, user = UserManager.login_user(args.username, args.password)
    if success:
        Session.login(user)
    print(message)
    return success


def show_portfolio_command(args):
    if not Session.is_logged_in():
        print("Сначала выполните login")
        return False
    
    user = Session.current_user
    portfolio = PortfolioManager.get_user_portfolio(user.user_id)
    
    if not portfolio or not portfolio.wallets:
        print("Ваш портфель пуст")
        return True
    
    base_currency = args.base.upper() if args.base else "USD"
    total_value = portfolio.get_total_value(base_currency)
    
    print(f"\nПортфель пользователя '{user.username}' (база: {base_currency}):")
    print("-" * 40)
    
    for wallet in portfolio.wallets.values():
        print(f"{wallet.currency_code}: {wallet.balance:.4f}")
    
    print("-" * 40)
    print(f"Итого в {base_currency}: {total_value:.2f}")
    
    return True


def buy_command(args):
    if not Session.is_logged_in():
        print("Сначала выполните login")
        return False
    
    user = Session.current_user
    success, message = PortfolioManager.buy_currency(user.user_id, args.currency.upper(), args.amount)
    print(message)
    return success


def sell_command(args):
    if not Session.is_logged_in():
        print("Сначала выполните login")
        return False
    
    user = Session.current_user
    success, message = PortfolioManager.sell_currency(user.user_id, args.currency.upper(), args.amount)
    print(message)
    return success


def get_rate_command(args):
    success, message, _ = RateManager.get_rate(args.from_currency.upper(), args.to_currency.upper())
    print(message)
    return success


def update_rates_command(args):
    updater = RatesUpdater()
    success = updater.run_update(args.source)
    
    if success:
        print("Курсы успешно обновлены")
    else:
        print("Не удалось обновить курсы")
    
    return success


def show_rates_command(args):
    import json
    from pathlib import Path
    
    rates_file = Path("data/rates.json")
    
    if not rates_file.exists():
        print("Локальный кеш курсов пуст. Выполните 'update-rates', чтобы загрузить данные.")
        return False
    
    with open(rates_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    pairs = data.get("pairs", {})
    last_refresh = data.get("last_refresh", "неизвестно")
    
    print(f"\nКурсы из кеша (обновлено: {last_refresh}):")
    print("-" * 50)
    
    for pair, info in pairs.items():
        print(f"{pair}: {info['rate']:.6f} ({info['source']})")
    
    return True


def create_parser():
    parser = argparse.ArgumentParser(description="ValutaTrade Hub - Платформа для торговли валютами")
    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")
    
    # Команда register
    register_parser = subparsers.add_parser("register", help="Регистрация нового пользователя")
    register_parser.add_argument("--username", required=True, help="Имя пользователя")
    register_parser.add_argument("--password", required=True, help="Пароль")
    
    # Команда login
    login_parser = subparsers.add_parser("login", help="Вход в систему")
    login_parser.add_argument("--username", required=True, help="Имя пользователя")
    login_parser.add_argument("--password", required=True, help="Пароль")
    
    # Команда show-portfolio
    portfolio_parser = subparsers.add_parser("show-portfolio", help="Показать портфель")
    portfolio_parser.add_argument("--base", help="Базовая валюта (по умолчанию: USD)")
    
    # Команда buy
    buy_parser = subparsers.add_parser("buy", help="Купить валюту")
    buy_parser.add_argument("--currency", required=True, help="Код валюты (например, BTC)")
    buy_parser.add_argument("--amount", type=float, required=True, help="Количество")
    
    # Команда sell
    sell_parser = subparsers.add_parser("sell", help="Продать валюту")
    sell_parser.add_argument("--currency", required=True, help="Код валюты")
    sell_parser.add_argument("--amount", type=float, required=True, help="Количество")
    
    # Команда get-rate
    rate_parser = subparsers.add_parser("get-rate", help="Получить курс валюты")
    rate_parser.add_argument("--from", dest="from_currency", required=True, help="Исходная валюта")
    rate_parser.add_argument("--to", dest="to_currency", required=True, help="Целевая валюта")
    
    # Команда update-rates
    update_parser = subparsers.add_parser("update-rates", help="Обновить курсы из API")
    update_parser.add_argument("--source", choices=["coingecko", "exchangerate"], help="Источник данных")
    
    # Команда show-rates
    show_rates_parser = subparsers.add_parser("show-rates", help="Показать курсы из кеша")
    show_rates_parser.add_argument("--currency", help="Показать только указанную валюту")
    
    return parser


def main():
    parser = create_parser()
    
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    args = parser.parse_args()
    
    # Сопоставление команд с функциями
    commands = {
        "register": register_command,
        "login": login_command,
        "show-portfolio": show_portfolio_command,
        "buy": buy_command,
        "sell": sell_command,
        "get-rate": get_rate_command,
        "update-rates": update_rates_command,
        "show-rates": show_rates_command,
    }
    
    if args.command in commands:
        success = commands[args.command](args)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()


def buy_command(args):
    """Команда покупки валюты"""
    if not Session.is_logged_in():
        print("Сначала выполните login")
        return False
    
    try:
        user = Session.current_user
        success, message = PortfolioManager.buy_currency(user.user_id, args.currency.upper(), args.amount)
        print(message)
        return success
    except ValutaTradeException as e:
        print(f"Ошибка: {str(e)}")
        return False
    
def list_currencies_command(args):
    """Показать список доступных валют"""
    print("\nДоступные валюты:")
    print("-" * 30)
    for code, info in CURRENCIES.items():
        print(f"{code}: {info['name']} ({info['type']})")
    return True

if __name__ == "__main__":
    main()