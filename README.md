# 🎮 Zetpar - Для фарма часов в Steam

```
███████╗███████╗████████╗██████╗  █████╗ ██████╗
╚══███╔╝██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗
  ███╔╝ █████╗     ██║   ██████╔╝███████║██████╔╝
 ███╔╝  ██╔══╝     ██║   ██╔═══╝ ██╔══██║██╔══██╗
███████╗███████╗   ██║   ██║     ██║  ██║██║  ██║
╚══════╝╚══════╝   ╚═╝   ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝
```

## 🚀 Что это вообще такое?

Zetpar - это консольный менеджер для Steam, который позволяет управлять сессиями игр прямо из терминала. Минимальные нагрузки на систему, игры в диспетчере не отображаются, а часики в стиме тикают. Кратко - фарм часов в Steam.

### 🎯 Фичи (которые реально работают (почти))

-  Авторизация в Steam (с поддержкой Steam Guard)
-  Сохранение профилей (потом доделаю фулл сессии)
-  Запуск/остановка игр (но не работает запуск нескольких игр, пока что)
-  Отслеживание времени в игре 
-  Стильный консольный интерфейс в стиле Steam 

## 🛠 Установка

### 🐍 Обычный способ

```bash
# Клонируем репозиторий
git clone https://github.com/noon05/Zetpar.git
cd zetpar

# Создаем виртуальное окружение (рекомендуется)
python -m venv venv
source venv/bin/activate  # Для Linux/Mac
venv\\Scripts\\activate   # Для Windows

# Устанавливаем зависимости
pip install -r requirements.txt

# Запускаем
python main.py
```

### 🐋 Docker (для любителей dro4ки)

```bash
# Собираем и запускаем
docker-compose up --build

# Для остановки
docker-compose down
```

## 🎮 Как пользоваться

1. Запускаем программу
2. Выбираем профиль или создаем новый
3. Логинимся в Steam (не забываем про Steam Guard, если требуется)
4. Используем команды:
   - `start <app_id>` - запустить игру
   - `stop <app_id>` - остановить игру
   - `stopall` - остановить все игры (когда мама зовет (если есть))
   - `help` - список команд
   - `exit` - выход

## 🔧 Технические детали

- Python 3.10
- Куча крутых библиотек (список в requirements.txt)
- Поддержка Docker (для тех, кто не терпила)

## 🤔 Зачем это нужно?

А почему бы и нет? На год на сервак поставил игрушку и нафармил 12к часов, чобы и нет

## 🐛 Известные баги

- Иногда Steam Guard код может быть капризным
- Steam API может внезапно решить не работать

## 🤝 Контрибьюция

Присылайте свои PR, если хотите сделать Zetpar лучше!
