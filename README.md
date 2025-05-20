# Multi-Agent Telegram Publisher 🤖📬

Автоматизированный бот для публикации статей в Telegram-канале с генерацией текста и иллюстраций через OpenAI, фактчекингом, хранением истории и уведомлением владельца.

---

## 📖 Содержание  
1. [Описание проекта](#описание-проекта)  
2. [Основные возможности](#основные-возможности)  
3. [Технологии](#технологии)  
4. [Установка](#установка)  
5. [Конфигурация](#конфигурация)  
6. [Запуск](#запуск)  
7. [Структура проекта](#структура-проекта)  
8. [Использование](#использование)  
9. [Требования к окружению](#требования-к-окружению)  
10. [Тестирование](#тестирование)  
11. [Советы по отладке](#советы-по-отладке)  
12. [Пожертвования и вклад](#пожертвования-и-вклад)  
13. [Лицензия](#лицензия)  

---

## 📦 Описание проекта  
Этот бот периодически подтягивает новые идеи из Google Sheets, генерирует на их основе черновик Telegram-поста и заголовок через ChatGPT, создаёт иллюстрацию через DALL·E, отправляет всё одним сообщением в канал, отмечает идею как «выполнено» и сохраняет текст в векторную память. После публикации бот уведомляет владельца канала о деталях поста.

---

## ✨ Основные возможности  
- **Автоматическая генерация текста** по шаблону из идей в Google Sheets  
- **Фактчекинг** и грамматическая коррекция через OpenAI + SerpAPI  
- **Генерация иллюстрации** (модель DALL·E 3 или DALL·E 2)  
- **Публикация единым сообщением**: заголовок, картинка, текст  
- **История публикаций** в Chroma (vector store) для быстрого поиска похожих тем  
- **Уведомление владельца** канала с подробностями  
- **Планировщик** (APScheduler + pytz) для гибкого расписания  

---

## 🛠 Технологии  
- Python 3.10+  
- langchain-openai  
- OpenAI API  
- Google Sheets API  
- ChromaDB  
- python-telegram-bot  
- APScheduler  
- pytz  
- PyYAML, gspread, oauth2client, SerpAPI  

---

## ⚙️ Установка

1. Клонировать репозиторий:  
   ```bash
   git clone https://github.com/<your-username>/multi-agent-publisher.git
   cd multi-agent-publisher
   ```
2. Создать и активировать виртуальное окружение:  
   ```bash
   python -m venv .venv
   source .venv/bin/activate    # Linux/macOS
   .venv\Scripts\activate     # Windows PowerShell
   ```
3. Установить зависимости:  
   ```bash
   pip install -r requirements.txt
   ```

---

## 🔧 Конфигурация

1. Переименуйте пример `config.example.yaml` в `config.yaml`.
2. Заполните поля в `config.yaml`:

   ```yaml
   openai:
     api_key: "<ваш OpenAI API ключ>"

   google_sheets:
     credentials_json: "path/to/credentials.json"
     sheet_id: "<Google Sheet ID>"
     worksheet_name: "work"

   serpapi:
     api_key: "<ваш SerpAPI ключ>"

   telegram:
     token: "<бот-токен>"
     channel_chat_id: -1001234567890
     channel_username: "my_channel"
     owner_chat_id: 123456789

   memory:
     persist_directory: "./chroma_db"
     collection_name: "publications"

   scheduling:
     timezone: "Europe/Moscow"
     jobs:
       - cron: "0 9 * * *"               # ежедневно в 09:00
       - cron: "30 18 * * mon,wed,fri"   # пн/ср/пт в 18:30
   ```
3. Убедитесь, что путь к `credentials_json` доступен боту.

---

## ▶️ Запуск

```bash
python main.py
```

---

## 📁 Структура проекта

```
├── tools/
│   ├── telegram_tool.py
│   ├── sheets_toolkit.py
│   ├── fact_checker.py
│   └── memory_store.py
├── template_prompt.py
├── main.py
├── config.yaml
├── requirements.txt
└── README.md
```

---

## 💡 Использование

- Добавьте новую идею (status = `ожидание`) в Google Sheets.
- Бот автоматически опубликует пост, отметит выполненным и уведомит владельца.

---

## 🧪 Тестирование

1. Добавьте тестовую строку в Google Sheets.
2. Запустите `main.py` и проверьте публикацию.

---

## 🔍 Советы по отладке

- Логи в консоли, уровень логирования можно изменить в `main.py`.
- Проверяйте корректность ключей и лимиты Telegram (1024 символа).

---

## 🤝 Вклад

Буду благодарен за звёздочки и pull-request'ы!

---

## 📜 Лицензия

MIT © 2025
