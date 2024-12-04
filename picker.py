"""
Изначальный говнокод
"""
import os
import sys
import time
import platform
from getpass import getpass
try:
    from steam.client import SteamClient
except ImportError:
    print("Установка необходимых зависимостей...")
    os.system('pip install -U steam[client]')
    from steam.client import SteamClient

def clear_screen():
    """Очистка экрана для разных ОС"""
    if platform.system().lower() == "windows":
        os.system('cls')
    else:
        os.system('clear')

def steam_idle(username, password, app_id):
    """
    Функция для эмуляции игровой сессии
    :param username: логин Steam
    :param password: пароль Steam
    :param app_id: ID игры в Steam
    """
    client = SteamClient()
    sentry_path = 'steam_sentry.bin'  
    
    try:
        if os.path.exists(sentry_path):
            client.set_credential_location(sentry_path)

        guard_code = input("Введите код Steam Guard из мобильного приложения (оставьте пустым, если не требуется): ")
        result = client.login(username=username, password=password, two_factor_code=guard_code)
        while result in (None, 'invalid_2fa'):
            guard_code = input("Неверный код. Введите код Steam Guard снова: ")
            result = client.login(username=username, password=password, two_factor_code=guard_code)
            
        if result != 1:
            print("Ошибка входа в Steam. Проверьте логин и пароль.")
            print(f"Код ошибки: {result}")
            return
        
        print(f"Успешный вход в Steam как {client.user.name}")
        print(f"Начинаем фармить часы в игре (App ID: {app_id})")
        client.games_played([app_id])
        
        start_time = time.time()
        try:
            while True:
                clear_screen()
                elapsed_time = int(time.time() - start_time)
                hours = elapsed_time // 3600
                minutes = (elapsed_time % 3600) // 60
                seconds = elapsed_time % 60
                
                print(f"Статус: Активно")
                print(f"Аккаунт: {client.user.name}")
                print(f"App ID: {app_id}")
                print(f"Время работы: {hours:02d}:{minutes:02d}:{seconds:02d}")
                print("\nНажмите Ctrl+C для выхода")
                
                if elapsed_time % 30 == 0:
                    client.games_played([app_id])

                client.run_forever()
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\nЗавершение работы...")
            
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    
    finally:
        client.games_played([]) 
        client.logout()
        print("Выход из Steam выполнен")

if __name__ == "__main__":
    clear_screen()
    print("Steam Idler - Программа для фарма часов в Steam")
    print("-" * 50)
    
    username = input("Введите логин Steam: ")
    password = getpass("Введите пароль Steam: ")
    app_id = input("Введите App ID игры: ")
    
    try:
        app_id = int(app_id)
    except ValueError:
        print("Ошибка: App ID должен быть числом")
        sys.exit(1)
    
    steam_idle(username, password, app_id)
