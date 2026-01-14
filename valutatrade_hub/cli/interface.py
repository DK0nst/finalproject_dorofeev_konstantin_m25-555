import argparse
import cmd
import shlex
import sys

from ..core.currencies import CURRENCIES
from ..core.exceptions import RegistrationError, ValutaTradeException
from ..core.usecases import PortfolioManager, RateManager, UserManager
from ..parser_service.updater import RatesUpdater


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


# ============================================================================
# ФУНКЦИИ КОМАНД (только для интерактивной оболочки)
# ============================================================================

def _register_command(args_list):
    """Команда регистрации"""
    parser = argparse.ArgumentParser(prog="register", add_help=False)
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    
    try:
        args = parser.parse_args(args_list)
        
        try:
            user_id = UserManager.register_user(args.username, args.password)
            print(f"Пользователь '{args.username}' зарегистрирован (id={user_id})")
        except RegistrationError as e:
            print(str(e))
    except SystemExit:
        pass  # Игнорируем выход из парсера
    except Exception as e:
        print(f"Ошибка: {str(e)}")


def _login_command(args_list):
    """Команда входа"""
    parser = argparse.ArgumentParser(prog="login", add_help=False)
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    
    try:
        args = parser.parse_args(args_list)
        
        success, message, user = UserManager.login_user(args.username, args.password)
        if success:
            Session.login(user)
        print(message)
    except SystemExit:
        pass
    except Exception as e:
        print(f"Ошибка: {str(e)}")


def _show_portfolio_command(args_list):
    """Команда показа портфеля"""
    if not Session.is_logged_in():
        print("Сначала выполните login")
        return
    
    parser = argparse.ArgumentParser(prog="portfolio", add_help=False)
    parser.add_argument("--base", help="Базовая валюта (по умолчанию: USD)")
    
    try:
        args = parser.parse_args(args_list)
        
        user = Session.current_user
        portfolio = PortfolioManager.get_user_portfolio(user.user_id)
        
        if not portfolio or not portfolio.wallets:
            print("Ваш портфель пуст")
            return
        
        base_currency = args.base.upper() if args.base else "USD"
        total_value = portfolio.get_total_value(base_currency)
        
        print(f"\nПортфель пользователя '{user.username}' (база: {base_currency}):")
        print("-" * 40)
        
        for wallet in portfolio.wallets.values():
            print(f"{wallet.currency_code}: {wallet.balance:.4f}")
        
        print("-" * 40)
        print(f"Итого в {base_currency}: {total_value:.2f}")
        
    except SystemExit:
        pass
    except Exception as e:
        print(f"Ошибка: {str(e)}")


def _buy_command(args_list):
    """Команда покупки валюты"""
    if not Session.is_logged_in():
        print("Сначала выполните login")
        return
    
    parser = argparse.ArgumentParser(prog="buy", add_help=False)
    parser.add_argument("--currency", required=True)
    parser.add_argument("--amount", type=float, required=True)
    
    try:
        args = parser.parse_args(args_list)
        
        user = Session.current_user
        success, message = PortfolioManager.buy_currency(
            user.user_id, args.currency.upper(), args.amount)
        print(message)
    except SystemExit:
        pass
    except ValutaTradeException as e:
        print(f"Ошибка: {str(e)}")
    except Exception as e:
        print(f"Ошибка: {str(e)}")

def _deposit_command(args_list):
    """Команда пополнения баланса"""
    if not Session.is_logged_in():
        print("Сначала выполните login")
        return
    
    parser = argparse.ArgumentParser(prog="deposit", add_help=False)
    parser.add_argument("--currency", required=True, 
                        help="Код валюты (например, USD)")
    parser.add_argument("--amount", type=float, required=True, 
                        help="Сумма пополнения")
    
    try:
        args = parser.parse_args(args_list)
        
        user = Session.current_user
        success, message = PortfolioManager.deposit_currency(
            user.user_id, args.currency.upper(), args.amount)
        print(message)
    except SystemExit:
        pass
    except Exception as e:
        print(f"Ошибка: {str(e)}")

def _sell_command(args_list):
    """Команда продажи валюты"""
    if not Session.is_logged_in():
        print("Сначала выполните login")
        return
    
    parser = argparse.ArgumentParser(prog="sell", add_help=False)
    parser.add_argument("--currency", required=True)
    parser.add_argument("--amount", type=float, required=True)
    
    try:
        args = parser.parse_args(args_list)
        
        user = Session.current_user
        success, message = PortfolioManager.sell_currency(
            user.user_id, args.currency.upper(), args.amount)
        print(message)
    except SystemExit:
        pass
    except Exception as e:
        print(f"Ошибка: {str(e)}")


def _get_rate_command(args_list):
    """Команда получения курса"""
    parser = argparse.ArgumentParser(prog="rate", add_help=False)
    parser.add_argument("--from", dest="from_currency", required=True)
    parser.add_argument("--to", dest="to_currency", required=True)
    
    try:
        args = parser.parse_args(args_list)
        
        success, message, _ = RateManager.get_rate(
            args.from_currency.upper(), args.to_currency.upper())
        print(message)
    except SystemExit:
        pass
    except Exception as e:
        print(f"Ошибка: {str(e)}")


def _update_rates_command(args_list):
    """Команда обновления курсов"""
    parser = argparse.ArgumentParser(prog="update", add_help=False)
    parser.add_argument("--source", choices=["coingecko", "exchangerate"], 
                       help="Источник данных")
    
    try:
        args = parser.parse_args(args_list)
        
        updater = RatesUpdater()
        success = updater.run_update(args.source)
        
        if success:
            print("Курсы успешно обновлены")
        else:
            print("Не удалось обновить курсы")
    except SystemExit:
        pass
    except Exception as e:
        print(f"Ошибка: {str(e)}")


def _show_rates_command(args_list):
    """Команда показа курсов"""
    parser = argparse.ArgumentParser(prog="show", add_help=False)
    parser.add_argument("--currency", help="Показать только указанную валюту")
    
    try:
        args = parser.parse_args(args_list)
        
        import json
        from pathlib import Path
        
        rates_file = Path("data/rates.json")
        
        if not rates_file.exists():
            print("Локальный кеш курсов пуст. Выполните 'update', чтобы загрузить данные.")
            return
        
        with open(rates_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        pairs = data.get("pairs", {})
        last_refresh = data.get("last_refresh", "неизвестно")
        
        print(f"\nКурсы из кеша (обновлено: {last_refresh}):")
        print("-" * 50)
        
        # Фильтрация по валюте, если указана
        for pair, info in pairs.items():
            if args.currency:
                if args.currency.upper() not in pair:
                    continue
            print(f"{pair}: {info['rate']:.6f} ({info['source']})")
    except SystemExit:
        pass
    except Exception as e:
        print(f"Ошибка: {str(e)}")


def _list_currencies_command(args_list):
    """Команда списка валют"""
    print("\nДоступные валюты:")
    print("-" * 30)
    for code, info in CURRENCIES.items():
        print(f"{code}: {info['name']} ({info['type']})")


# ============================================================================
# ИНТЕРАКТИВНАЯ ОБОЛОЧКА
# ============================================================================

class ValutaTradeShell(cmd.Cmd):
    """Интерактивная оболочка ValutaTrade Hub"""
    
    intro = """
╔═══════════════════════════════════════════╗
║      Добро пожаловать в ValutaTrade Hub   ║
║        Интерактивный режим                ║
║   Введите help для списка команд          ║
╚═══════════════════════════════════════════╝
"""
    prompt = "valutatrade> "
    
    def emptyline(self):
        """При пустой строке ничего не делаем"""
        pass

    def do_deposit(self, args):
        """Пополнить баланс: deposit --currency CODE --amount AMOUNT"""
        _deposit_command(shlex.split(args))
        return False
    
    def do_register(self, args):
        """Регистрация нового пользователя: register --username NAME --password PASS"""
        _register_command(shlex.split(args))
        return False  # Важно: возвращаем False, чтобы не выходить из оболочки
    
    def do_login(self, args):
        """Вход в систему: login --username NAME --password PASS"""
        _login_command(shlex.split(args))
        return False
    
    def do_logout(self, args):
        """Выход из системы"""
        Session.logout()
        print("Вы вышли из системы")
        return False
    
    def do_portfolio(self, args):
        """Показать портфель: portfolio [--base CURRENCY]"""
        _show_portfolio_command(shlex.split(args))
        return False
    
    def do_buy(self, args):
        """Купить валюту: buy --currency CODE --amount AMOUNT"""
        _buy_command(shlex.split(args))
        return False
    
    def do_sell(self, args):
        """Продать валюту: sell --currency CODE --amount AMOUNT"""
        _sell_command(shlex.split(args))
        return False
    
    def do_rate(self, args):
        """Получить курс: rate --from CURRENCY --to CURRENCY"""
        _get_rate_command(shlex.split(args))
        return False
    
    def do_update(self, args):
        """Обновить курсы: update [--source coingecko|exchangerate]"""
        _update_rates_command(shlex.split(args))
        return False
    
    def do_show(self, args):
        """Показать курсы: show [--currency CODE]"""
        _show_rates_command(shlex.split(args))
        return False
    
    def do_list(self, args):
        """Показать список валют"""
        _list_currencies_command(shlex.split(args))
        return False
    
    def do_whoami(self, args):
        """Показать текущего пользователя"""
        if Session.is_logged_in():
            user = Session.current_user
            print(f"Вы вошли как: {user._username}")
            print(f"ID пользователя: {user._user_id}")
        else:
            print("Вы не вошли в систему")
        return False
    
    def do_clear(self, args):
        """Очистить экран"""
        print("\033[H\033[J", end="")
        return False
    
    def do_exit(self, args):
        """Выход из программы"""
        print("До свидания!")
        return True  # Только exit возвращает True
    
    def do_quit(self, args):
        """Выход из программы"""
        return self.do_exit(args)
    
    def do_help(self, args):
        """Показать справку по командам"""
        print("\n" + "="*60)
        print("Доступные команды:")
        print("="*60)
        print("\n📝 Управление пользователями:")
        print("  register --username NAME --password PASS  - Регистрация")
        print("  login --username NAME --password PASS     - Вход")
        print("  logout                                   - Выход")
        print("  whoami                                   - Текущий пользователь")
        
        print("\n💰 Торговля:")
        print("  deposit --currency CODE --amount AMOUNT  - Пополнить баланс")
        print("  buy --currency CODE --amount AMOUNT      - Купить валюту")
        print("  sell --currency CODE --amount AMOUNT     - Продать валюту")
        print("  portfolio [--base CURRENCY]             - Показать портфель")
        
        print("\n📊 Курсы валют:")
        print("  rate --from CODE --to CODE              - Получить курс")
        print("  show [--currency CODE]                  - Показать все курсы")
        print("  update [--source coingecko|exchangerate] - Обновить курсы")
        print("  list                                    - Список валют")
        
        print("\n⚙️  Системные:")
        print("  clear                                   - Очистить экран")
        print("  help [КОМАНДА]                         - Справка")
        print("  exit, quit                             - Выход")
        print("="*60)
        print("\nПримеры:")
        print("  register --username alice --password 123456")
        print("  login --username alice --password 123456")
        print("  deposit --currency USD --amount 10000")
        print("  update                                  # Получить курсы")
        print("  buy --currency BTC --amount 0.01")
        print("  rate --from USD --to BTC")
        print("="*60)
        return False
    
    def preloop(self):
        """Выполняется перед началом цикла"""
        print("Для справки введите: help")
    
    def postloop(self):
        """Выполняется после выхода из цикла"""
        print("Спасибо за использование ValutaTrade Hub!")


def main():
    """Главная функция - всегда запускает интерактивную оболочку"""
    try:
        shell = ValutaTradeShell()
        shell.cmdloop()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"Ошибка при запуске оболочки: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()