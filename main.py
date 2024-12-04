"""
Главный файл приложения Zetpar
"""
import os
import time
import threading
import platform
from getpass import getpass
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from zoblako.core.steam_client import SteamManager
from zoblako.ui.console import ConsoleUI
from zoblako.core.profile_manager import ProfileManager
import sys
import colorama
colorama.init()

def clear_screen():
    """Очистка экрана для разных ОС"""
    if platform.system().lower() == "windows":
        os.system('cls')
    else:
        os.system('clear')

def print_help(console_ui):
    """Вывод списка команд"""
    commands = {
        "start <app_id>": "Запустить игру",
        "stop <app_id>": "Остановить игру",
        "stopall": "Остановить все игры",
        "help": "Показать это сообщение",
        "exit": "Выйти из программы"
    }
    help_text = Text()
    help_text.append("\nДоступные команды:", style="steam_blue")
    
    for cmd, desc in commands.items():
        help_text.append(f"\n  {cmd:<15}", style="steam_gray")
        help_text.append(f" - {desc}", style="steam_blue")
    
    help_text.append("\n")
    console_ui.console.print(Panel(help_text, border_style="steam_blue"))

def handle_command(cmd, steam_manager, console_ui):
    """Обработка команд пользователя"""
    cmd = cmd.strip().lower()
    
    if cmd == "help":
        print_help(console_ui)
        return True
    elif cmd == "exit":
        return False
    elif cmd == "stopall":
        steam_manager.stop_all_games()
        console_ui.display_success("Все игры остановлены")
        return True
    elif cmd.startswith("start "):
        try:
            app_id = int(cmd.split(" ")[1]) 
            success, message = steam_manager.start_game(app_id)
            if success:
                console_ui.display_success(message)
            else:
                console_ui.display_error(message)
        except ValueError:
            console_ui.display_error("Неверный формат App ID. Используйте только цифры.")
        except IndexError:
            console_ui.display_error("Укажите App ID игры")
        return True
    elif cmd.startswith("stop "):
        try:
            app_id = int(cmd.split(" ")[1])  
            success, message = steam_manager.stop_game(app_id)
            if success:
                console_ui.display_success(message)
            else:
                console_ui.display_error(message)
        except ValueError:
            console_ui.display_error("Неверный формат App ID. Используйте только цифры.")
        except IndexError:
            console_ui.display_error("Укажите App ID игры")
        return True
    else:
        console_ui.display_error("Неизвестная команда. Введите 'help' для списка команд")
        return True

def update_ui(steam_manager, console_ui, should_run):
    """Обновление интерфейса"""
    last_update = 0
    update_interval = 5  
    
    while should_run[0]:
        try:
            current_time = time.time()
            if current_time - last_update >= update_interval:
                session_info = steam_manager.get_session_info()
                games_info = steam_manager.get_current_games()
                console_ui.update_display(session_info, games_info)
                last_update = current_time
            time.sleep(0.1)  
        except Exception as e:
            print(f"Ошибка обновления интерфейса: {e}")
            time.sleep(5)

def handle_commands(steam_manager, console_ui, should_run):
    """Поток обработки команд"""
    while should_run[0]:
        try:
            cmd = input("\n> ").strip()
            if not cmd:  
                continue
            if not handle_command(cmd, steam_manager, console_ui):
                should_run[0] = False
                break
        except Exception as e:
            console_ui.display_error(f"Ошибка обработки команды: {e}")

def get_styled_input(console_ui, prompt, password=False):
    """Получение ввода с стилизацией Steam"""
    try:
        console_ui.console.print(Panel(prompt, style="steam_blue", border_style="steam_blue"))
        if password:
            return getpass("> ")
        return input("> ")
    except KeyboardInterrupt:
        print("\n")
        console_ui.display_error("Вы завершили программу.")
        sys.exit(0)

def select_profile(profile_manager, console_ui):
    """Выбор профиля"""
    profiles = profile_manager.get_profiles()
    
    if not profiles:
        return None, None
        
    console_ui.console.print(Panel("Выберите профиль или введите 'new' для создания нового:", 
                                 style="steam_blue", border_style="steam_blue"))
    
    for i, profile in enumerate(profiles, 1):
        console_ui.console.print(f"{i}. {profile}")
    
    while True:
        choice = get_styled_input(console_ui, "Выбор профиля").lower()
        
        if choice == 'new':
            return None, None
            
        try:
            index = int(choice) - 1
            if 0 <= index < len(profiles):
                username = profiles[index]
                password = profile_manager.load_profile(username)
                return username, password
        except ValueError:
            pass
            
        console_ui.display_error("Неверный выбор. Попробуйте снова.")

def main():
    steam_manager = SteamManager()
    console_ui = ConsoleUI()
    profile_manager = ProfileManager()
    
    clear_screen()
    
    banner = """[steam_blue]
███████╗███████╗████████╗██████╗  █████╗ ██████╗ 
╚══███╔╝██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗
  ███╔╝ █████╗     ██║   ██████╔╝███████║██████╔╝
 ███╔╝  ██╔══╝     ██║   ██╔═══╝ ██╔══██║██╔══██╗
███████╗███████╗   ██║   ██║     ██║  ██║██║  ██║
╚══════╝╚══════╝   ╚═╝   ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝[/]"""
    
    console_ui.console.print(banner)
    console_ui.console.print(Panel("Steam Game Manager", style="steam_blue", border_style="steam_blue"))
    username, password = select_profile(profile_manager, console_ui)
    if not username:
        username = get_styled_input(console_ui, "Логин Steam")
        password = get_styled_input(console_ui, "Пароль Steam", password=True)
        save = get_styled_input(console_ui, "Сохранить профиль? (y/n)").lower() == 'y'
        if save:
            if profile_manager.save_profile(username, password):
                console_ui.display_success("Профиль сохранен")
            else:
                console_ui.display_error("Не удалось сохранить профиль")

    if not steam_manager.authenticate(username, password, console_ui):
        console_ui.display_error("Ошибка авторизации")
        return
    print_help(console_ui)
    should_run = [True]
    ui_thread = threading.Thread(
        target=update_ui,
        args=(steam_manager, console_ui, should_run),
        daemon=True
    )
    ui_thread.start()
    cmd_thread = threading.Thread(
        target=handle_commands,
        args=(steam_manager, console_ui, should_run),
        daemon=True
    )
    cmd_thread.start()
    try:
        while should_run[0]:
            steam_manager.update_status()
    except KeyboardInterrupt:
        steam_manager.logout()
        sys.exit(0)
    except Exception as e:
        console_ui.display_error(f"Ошибка обновления статуса Steam: {e}")
        time.sleep(1)
    
if __name__ == "__main__":
    main()
