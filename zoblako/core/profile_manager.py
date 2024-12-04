"""
Модуль для управления профилями пользователей
"""
import os
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class ProfileManager:
    def __init__(self):
        self.profiles_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'profiles')
        self.profiles_file = os.path.join(self.profiles_dir, 'profiles.json')
        self._ensure_profiles_dir()
        self.key = self._generate_key()
        self.fernet = Fernet(self.key)
        
    def _ensure_profiles_dir(self):
        """Создание директории для профилей если она не существует"""
        os.makedirs(self.profiles_dir, exist_ok=True)
        if not os.path.exists(self.profiles_file):
            with open(self.profiles_file, 'w') as f:
                json.dump({}, f)
                
    def _generate_key(self):
        """Генерация ключа шифрования"""
        salt = b'zetpar_salt'  # В реальном приложении следует использовать случайную соль
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(b'zetpar_key'))  # В реальном приложении следует использовать случайный ключ
        return key
        
    def save_profile(self, username, password):
        """Сохранение профиля"""
        try:
            with open(self.profiles_file, 'r') as f:
                profiles = json.load(f)
                
            # Шифруем пароль
            encrypted_password = self.fernet.encrypt(password.encode()).decode()
            
            # Сохраняем профиль
            profiles[username] = {
                'password': encrypted_password
            }
            
            with open(self.profiles_file, 'w') as f:
                json.dump(profiles, f)
                
            return True
        except Exception:
            return False
            
    def load_profile(self, username):
        """Загрузка профиля"""
        try:
            with open(self.profiles_file, 'r') as f:
                profiles = json.load(f)
                
            if username in profiles:
                # Расшифровываем пароль
                encrypted_password = profiles[username]['password'].encode()
                password = self.fernet.decrypt(encrypted_password).decode()
                return password
            return None
        except Exception:
            return None
            
    def get_profiles(self):
        """Получение списка сохраненных профилей"""
        try:
            with open(self.profiles_file, 'r') as f:
                profiles = json.load(f)
            return list(profiles.keys())
        except Exception:
            return []
            
    def delete_profile(self, username):
        """Удаление профиля"""
        try:
            with open(self.profiles_file, 'r') as f:
                profiles = json.load(f)
                
            if username in profiles:
                del profiles[username]
                
                with open(self.profiles_file, 'w') as f:
                    json.dump(profiles, f)
                return True
            return False
        except Exception:
            return False
