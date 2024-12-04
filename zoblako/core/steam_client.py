"""
Модуль для работы с Steam API и авторизацией
"""
import os
import sys
import time
import requests
from datetime import datetime
from steam.client import SteamClient
from rich.console import Console
from rich.panel import Panel

class SteamManager:
    """Основные методы для управления сессией и игрушками"""

    STEAM_STORE_API = "https://store.steampowered.com/api/appdetails"
    
    def __init__(self):
        self.client = SteamClient()
        self.sentry_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sentry')
        self.running_games = {}  
        self.should_run = True
        self.console = None  # Будет установлена при авторизации
        self.game_names_cache = {}  
        os.makedirs(self.sentry_path, exist_ok=True)
        
    def get_game_name(self, app_id):
        """Получение названия игры по app_id"""
        # Проверяем кэш
        if app_id in self.game_names_cache:
            return self.game_names_cache[app_id]
            
        try:
           
            params = {
                "appids": app_id,
                "l": "russian"  # Я бы не сказал, что это имеет смысл кнч...
            }
            response = requests.get(self.STEAM_STORE_API, params=params)
            data = response.json()
            
            if str(app_id) in data and data[str(app_id)]["success"]:
                game_name = data[str(app_id)]["data"]["name"]
                self.game_names_cache[app_id] = game_name
                return game_name
        except Exception as e:
            if self.console:
                self.console.print(Panel(f"Ошибка получения названия игры: {e}", 
                                       style="steam_red", border_style="steam_red"))
        
        # Если что-то пошло не так, возвращаем ID
        return f"Game {app_id}"
        
    def set_credential_location(self, username): #Я к слову забил на это, мб потом доделаю, можете ветки допилить если хотите)
        """Установка пути для sentry-файла"""
        sentry_file = os.path.join(self.sentry_path, f"{username}.sentry")
        self.client.set_credential_location(sentry_file)
        return sentry_file
    
    def authenticate(self, username, password, console_ui):
        """Аутентификация пользователя"""
        self.console = console_ui.console  
        sentry_file = self.set_credential_location(username)
        
        def get_guard_code():
            """Запрос кода Steam Guard"""
            self.console.print(Panel("Введите код Steam Guard из мобильного приложения (оставьте пустым, если не требуется)", 
                                   style="steam_blue", border_style="steam_blue"))
            return input("> ")
        
        # Здесь я чет не познал, в теории можно была отрисовывать qr, но это без меня
        guard_code = get_guard_code()
        
        # Реализация первой попытки аутентификации
        result = self.client.login(username=username, password=password, two_factor_code=guard_code)
        
        # Повторный запрос кода, если ты баклан
        while result in (None, 'invalid_2fa'):
            self.console.print(Panel("Неверный код. Введите код Steam Guard снова", 
                                   style="steam_red", border_style="steam_red"))
            guard_code = input("> ")
            result = self.client.login(username=username, password=password, two_factor_code=guard_code)
        
        if result != 1:
            self.console.print(Panel(f"Ошибка входа в Steam. Проверьте логин и пароль. (Код ошибки: {result})", 
                                   style="steam_red", border_style="steam_red"))
            return False
            
        self.console.print(Panel(f"Успешный вход в Steam как {self.client.user.name}", 
                               style="steam_green", border_style="steam_green"))
        return True
    
    def start_game(self, app_id):
        """Запуск игры"""
        try:
            app_id = int(app_id)
            if not self.client.connected:
                return False, "Нет подключения к Steam"
                
            # Останавливаем все текущие игры (только в теории, на практике у меня ток 1 игра и запускается:))
            self.stop_all_games()
            game_name = self.get_game_name(app_id)
            
            self.running_games[app_id] = {
                "start_time": datetime.now(),
                "name": game_name
            }
            
            # Тута игрушку запускаем
            self.client.games_played([app_id])
            
            return True, f"Игра {game_name} запущена"
            
        except ValueError:
            return False, "Неверный формат App ID"
        except Exception as e:
            self.console.print(Panel(f"Ошибка при запуске игры: {e}", 
                                   style="steam_red", border_style="steam_red"))
            return False, f"Ошибка при запуске игры: {e}"
    
    def stop_game(self, app_id):
        """Остановка игры"""
        try:
            app_id = int(app_id)
            if app_id in self.running_games:
                game_name = self.running_games[app_id]["name"]
                del self.running_games[app_id]
                if self.running_games:
                    self.client.games_played(list(self.running_games.keys()))
                else:
                    self.client.games_played([])
                return True, f"Игра {game_name} остановлена"
            return False, "Игра не запущена"
        except ValueError:
            return False, "Неверный формат App ID"
        except Exception as e:
            self.console.print(Panel(f"Ошибка при остановке игры: {e}", 
                                   style="steam_red", border_style="steam_red"))
            return False, f"Ошибка при остановке игры: {e}"
    
    def stop_all_games(self):
        """Остановка всех игр"""
        self.running_games.clear()
        if self.client.connected:
            self.client.games_played([])
            
    def get_current_games(self):
        """Получение списка текущих игр"""
        if not self.client.connected:
            return []
        
        games = []
        for game_id, game_data in self.running_games.items():
            game_info = {
                "id": game_id,
                "name": game_data["name"],
                "start_time": game_data["start_time"].strftime("%H:%M:%S"),
                "play_time": self.get_play_time(game_data["start_time"])
            }
            games.append(game_info)
        return games
    
    def get_play_time(self, start_time):
        """Расчет времени в игре"""
        delta = datetime.now() - start_time
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def get_session_info(self):
        """Получение информации о текущей сессии"""
        if not self.client.connected:
            return {"status": "Не в сети"}
        
        return {
            "status": "В сети",
            "username": self.client.user.name,
            "steam_id": self.client.steam_id,
            "games_running": len(self.running_games)
        }
    
    def update_status(self):
        """Обновление статуса игр и поддержание соединения"""
        try:
            # Обновляем статус игр
            if self.running_games and self.client.connected:
                game_ids = list(self.running_games.keys())
                if game_ids:
                    self.client.games_played(game_ids)

            self.client.run_forever() # Эту штуку не менять,
                                      # потому что либа кусок говна на gevent и по другому поддерживать не получится

        except KeyboardInterrupt:
            
            if self.console:
                self.console.print(
                    Panel("Программа прервана пользователем.", style="steam_red", border_style="steam_red")
                )
            sys.exit(0)


        except Exception as e:
            if self.console:
                self.console.print(Panel(f"Ошибка обновления статуса: {e}", 
                                       style="steam_red", border_style="steam_red"))
            time.sleep(1)
                     
            
    def logout(self):
        """Выход из Steam"""
        if self.client.connected:
            self.stop_all_games()
            self.client.logout()
            if self.console:
                self.console.print(Panel("Выход из Steam выполнен", 
                                       style="steam_green", border_style="steam_green"))
                self.console.print(Panel("Завершение работы...", 
                                       style="steam_blue", border_style="steam_blue"))
