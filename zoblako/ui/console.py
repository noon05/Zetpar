"""
Модуль для работы с консольным интерфейсом
"""
import os
from rich.console import Console
from rich.table import Table
from rich.theme import Theme
from rich.style import Style
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout

# Тема Steam
class ConsoleUI:
    """Класс консольного интерфейса"""
    
    def __init__(self):
        # Создаем тему Steam
        self.steam_theme = Theme({
            "steam_blue": "#1b2838",  
            "steam_gray": "#c7d5e0",  
            "steam_green": "#5c7e10", 
            "steam_red": "#c94a4a",  
            "info": "cyan",
            "warning": "yellow",
            "error": "red",
            "success": "green",
        })
        self.console = Console(theme=self.steam_theme)
        self.layout = Layout()
        self.last_session_data = None
        self.last_games_data = None
        
    def clear_screen(self):
        """Очистка экрана"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def create_session_table(self, session_data):
        """Создание таблицы с информацией о сессии"""
        table = Table(title="[steam_blue]Информация о сессии[/]", border_style="steam_blue")
        table.add_column("Параметр", style="steam_gray")
        table.add_column("Значение", style="steam_blue")
        
        for key, value in session_data.items():
            table.add_row(key, str(value))
            
        return table
        
    def create_games_table(self, games_data):
        """Создание таблицы с играми"""
        table = Table(title="[steam_blue]Запущенные игры[/]", border_style="steam_blue")
        table.add_column("ID", style="steam_gray")
        table.add_column("Название", style="steam_blue")
        table.add_column("Время запуска", style="info")
        table.add_column("Время в игре", style="success")
        
        if games_data:
            for game in games_data:
                table.add_row(
                    str(game.get("id", "")),
                    game.get("name", ""),
                    game.get("start_time", ""),
                    game.get("play_time", "")
                )
        else:
            table.add_row("", "[steam_gray]Нет запущенных игр[/]", "", "")
            
        return table
        
    def update_display(self, session_data=None, games_data=None):
        """Обновление отображения"""
        if session_data is not None:
            self.last_session_data = session_data
        if games_data is not None:
            self.last_games_data = games_data
            
        if self.last_session_data:
            self.clear_screen()
            self.console.print(self.create_session_table(self.last_session_data))
        if self.last_games_data is not None:
            self.console.print(self.create_games_table(self.last_games_data))
        
    def display_session_info(self, session_data):
        """Отображение информации о текущей сессии"""
        self.update_display(session_data=session_data)
        
    def display_running_games(self, games_data):
        """Отображение списка запущенных игр"""
        self.update_display(games_data=games_data)
        
    def display_error(self, message):
        """Отображение ошибки"""
        self.console.print(Panel(
            f"[error]{message}[/]",
            title="Ошибка",
            border_style="error"
        ))
        
    def display_success(self, message):
        """Отображение успешного действия"""
        self.console.print(Panel(
            f"[success]{message}[/]",
            title="Успешно",
            border_style="success"
        ))
        
    def display_prompt(self):
        """Отображение приглашения для ввода"""
        self.console.print("\n[steam_blue]Введите команду (help - справка):[/] ", end="")
        
    @property
    def theme(self):
        """Получение темы Steam"""
        return self.steam_theme
