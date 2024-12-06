from colorama import init, Fore, Style

# Инициализация colorama
init(autoreset=True)

# Функции для быстрого добавления префиксов и цветов

def success(message: str) -> str:
    """Префикс и зеленый цвет для успешных сообщений."""
    return f"{Fore.GREEN}{Style.BRIGHT}[SUCCESS] {message}"

def error(message: str) -> str:
    """Префикс и красный цвет для сообщений об ошибке."""
    return f"{Fore.RED}{Style.BRIGHT}[ERROR] {message}"

def warning(message: str) -> str:
    """Префикс и желтый цвет для предупреждений."""
    return f"{Fore.YELLOW}{Style.BRIGHT}[WARNING] {message}"

def info(message: str) -> str:
    """Префикс и синий цвет для информационных сообщений."""
    return f"{Fore.BLUE}{Style.BRIGHT}[INFO] {message}"

def debug(message: str) -> str:
    """Префикс и серый цвет для отладочных сообщений."""
    return f"{Fore.WHITE}{Style.BRIGHT}[DEBUG] {message}"
