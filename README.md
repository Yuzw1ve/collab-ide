# Collaborative Web IDE MVP

Совместная веб-IDE в реальном времени для групповой работы над кодом.  
Проект позволяет нескольким пользователям одновременно редактировать один файл, видеть участников сессии, получать AI-review, запускать код и получать Telegram-уведомления.

---

## Возможности

- Совместное редактирование кода в одной комнате
- WebSocket-синхронизация между участниками
- Список участников и позиции курсоров
- Лента событий
- AI review кода
- Auto AI review по debounce
- Запуск Python / JavaScript кода
- Leaderboard участников
- Incognito mode
- Telegram notifications

---

## Технологии

### Frontend

- React
- Vite
- JavaScript
- react-router-dom
- Monaco Editor (`@monaco-editor/react`)
- WebSocket
- Fetch API
- CSS

### Backend

- Python
- FastAPI
- WebSocket
- Uvicorn
- Pydantic
- Requests

### Дополнительно

- Telegram Bot API
- In-memory storage
- Python subprocess / Node.js execution

---

## Важное замечание по Python

Для backend рекомендуется использовать:

```txt
Python 3.11

Проект может работать нестабильно на слишком новых версиях Python, например 3.14.

Требования перед запуском
Убедитесь, что у вас установлены:

Python 3.11
Node.js 18+ и npm
node в PATH для запуска JavaScript-кода
python / python3 в PATH для запуска Python-кода
Структура проекта
Bash

collab-ide/
├── backend/
│   ├── main.py
│   ├── room_manager.py
│   ├── websocket_handlers.py
│   ├── telegram_notifier.py
│   ├── requirements.txt
│   ├── ai/
│   │   ├── ai_router.py
│   │   ├── ai_reviewer.py
│   │   ├── mock_review.py
│   │   └── prompt_builder.py
│   └── runner/
│       ├── run_router.py
│       └── code_runner.py
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       ├── styles.css
│       ├── pages/
│       ├── components/
│       ├── services/
│       └── utils/
│
└── README.md
Локальный запуск проекта
Проект запускается в двух терминалах:

Терминал 1 — backend
Терминал 2 — frontend
Шаг 1. Запуск backend
Открой первый терминал и перейди в папку backend:

Bash

cd backend
Создание виртуального окружения
Windows
Если Python 3.11 уже установлен:

Bash

py -3.11 -m venv venv
Linux / macOS
Bash

python3.11 -m venv venv
Активация виртуального окружения
Windows
Bash

venv\Scripts\activate
Linux / macOS
Bash

source venv/bin/activate
Установка зависимостей backend
Bash

pip install -r requirements.txt
Опционально: Telegram env-переменные
Если хотите включить Telegram notifications, перед запуском backend задайте переменные окружения.

Windows PowerShell
PowerShell

$env:TELEGRAM_BOT_TOKEN="your_bot_token_here"
$env:TELEGRAM_CHAT_IDS="123456789,987654321"
Linux / macOS
Bash

export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_CHAT_IDS="123456789,987654321"
Если эти переменные не заданы, проект все равно работает, просто без Telegram-уведомлений.

Опционально: внешний AI API
Если хотите использовать внешний LLM API вместо mock-review, задайте:

Windows PowerShell
PowerShell

$env:AI_REVIEWER_API_KEY="your_api_key"
$env:AI_REVIEWER_API_ENDPOINT="https://your-llm-endpoint.com/v1/chat/completions"
$env:AI_REVIEWER_MODEL="gpt-4o-mini"
$env:AI_REVIEWER_TIMEOUT="20"
Linux / macOS
Bash

export AI_REVIEWER_API_KEY="your_api_key"
export AI_REVIEWER_API_ENDPOINT="https://your-llm-endpoint.com/v1/chat/completions"
export AI_REVIEWER_MODEL="gpt-4o-mini"
export AI_REVIEWER_TIMEOUT="20"
Если эти переменные не заданы, AI review будет работать в mock/fallback режиме.

Запуск backend-сервера
Из папки backend/:

Bash

uvicorn main:app --reload
После запуска backend будет доступен на:

txt

http://localhost:8000
Проверка backend
Открой в браузере:

Health
txt

http://localhost:8000/health
Ожидаемый ответ:

JSON

{"status":"ok"}
Swagger docs
txt

http://localhost:8000/docs
Room API
txt

http://localhost:8000/api/rooms/test-room
Шаг 2. Запуск frontend
Открой второй терминал и перейди в папку frontend:

Bash

cd frontend
Установка зависимостей frontend
Bash

npm install
Запуск frontend
Bash

npm run dev
После запуска frontend будет доступен на:

txt

http://localhost:3000
Как пользоваться приложением
Вход в комнату
Открой:
txt

http://localhost:3000
Введи:
Username
Room ID
При необходимости включи:
Join in incognito mode
Нажми:
Join Room
Проверка совместной работы
Тест в двух вкладках
Открой две вкладки браузера
В первой зайди как:
Alice, room1
Во второй:
Bob, room1
Проверь:

оба участника отображаются в Participants
изменения кода синхронизируются
event log обновляется
leaderboard обновляется
AI Review
Введи в редакторе, например:

Python

eval(input())
print("debug")
Подожди ~2.5 секунды:

AI review должен обновиться автоматически
Или нажми кнопку Review.

Run Code
Пример для Python:

Python

print("Hello from runner")
Нажми Run.

Ожидается:

stdout показывает результат
leaderboard обновляется при успешном запуске
Telegram Notifications
Если Telegram env заданы, бот отправляет уведомления при:

join
leave
run
high severity AI issue
Как получить Telegram chat IDs
Создать бота через BotFather
Написать боту /start
Открыть:
txt

https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
Найти в JSON поле:
JSON

"chat": {
  "id": 123456789
}
Если нужно несколько пользователей, собрать несколько chat id и передать их через:

env

TELEGRAM_CHAT_IDS=123456789,987654321
Поведение AI review
Проект поддерживает два режима:

1. Mock / fallback режим
Работает без внешнего API и умеет находить:

eval
exec
print / console.log
debugger
пустой except
базовые merge suggestions
2. Внешний AI API
Используется, если заданы env-переменные:

AI_REVIEWER_API_KEY
AI_REVIEWER_API_ENDPOINT
Система leaderboard
Баллы начисляются так:

join room = +1
successful run = +3
Баллы не начисляются:

за редактирование
за неуспешный запуск
Частые проблемы
Backend не стартует
Проверь:

используешь ли Python 3.11
установлен ли venv правильно
выполнено ли:
Bash

pip install -r requirements.txt
Ошибка ModuleNotFoundError: requests
Установи зависимости backend:

Bash

pip install -r requirements.txt
Telegram не шлет уведомления
Проверь:

бот создан
ему написали /start
chat ids указаны правильно
env заданы до запуска backend
JavaScript run не работает
Проверь, что node установлен и доступен в PATH.

Python run не работает
Проверь, что python или python3 установлен и доступен в PATH.

Frontend открывается, но не работает realtime
Проверь:

backend реально запущен на localhost:8000
frontend реально запущен на localhost:3000
WebSocket endpoint доступен:
txt

ws://localhost:8000/ws/rooms/{roomId}?username={username}&displayName={displayName}
Краткий сценарий запуска
Терминал 1 — backend
Bash

cd backend
py -3.11 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
Терминал 2 — frontend
Bash

cd frontend
npm install
npm run dev


Быстрый тест
Запустить backend
Запустить frontend
Открыть http://localhost:3000
Зайти в одну комнату в двух вкладках
Проверить:
participants
sync кода
AI review
run output
leaderboard
```
