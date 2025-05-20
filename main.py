# main.py — интеграция компонентов и Scheduler с поддержкой pytz

import os
import yaml
import logging
import asyncio
import sys
from pathlib import Path
from datetime import datetime

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tools.sheets_toolkit import GoogleSheetsToolkit
from tools.telegram_tool import TelegramTool
from tools.fact_checker import FactChecker
from tools.memory_store import MemoryStore

from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper

from template_prompt import idea, headline_idea, grammar, image_post

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Загрузка конфигурации
CONFIG_PATH = Path(__file__).parent / 'config.yaml'
if not CONFIG_PATH.exists():
    logger.error("Config file not found: %s", CONFIG_PATH)
    sys.exit(1)
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# Telegram
telegram_cfg = config.get('telegram', {})
bot_token = telegram_cfg.get('token') or telegram_cfg.get('bot_token')
CHANNEL_ID = int(telegram_cfg.get('channel_chat_id') or telegram_cfg.get('chat_id'))
CHANNEL_USERNAME = telegram_cfg.get('channel_username')
OWNER_CHAT_ID = int(telegram_cfg.get('owner_chat_id'))

# Инициализация инструментов
sheets_cfg = config.get('google_sheets', {})
sheets_tool = GoogleSheetsToolkit(
    credentials_json=sheets_cfg['credentials_json'],
    sheet_id=sheets_cfg['sheet_id'],
    worksheet_name=sheets_cfg.get('worksheet_name', 'work')
)
fact_checker = FactChecker(
    openai_api_key=config['openai']['api_key'],
    serpapi_api_key=config.get('serpapi', {}).get('api_key')
)
memory_store = MemoryStore(
    persist_directory=config['memory']['persist_directory'],
    collection_name=config['memory']['collection_name'],
    openai_api_key=config['openai']['api_key']
)
telegram_tool = TelegramTool(token=bot_token)

# Шаблоны промптов
post_prompt = PromptTemplate(
    input_variables=['idea', 'examples'],
    template= idea
)
headline_prompt = PromptTemplate(
    input_variables=['text'],
    template=headline_idea
)

# Инициализация LLM и цепочек
llm_text = ChatOpenAI(
    openai_api_key=config['openai']['api_key'],
    model_name='gpt-4o',
    temperature=0.5
)
post_chain = LLMChain(llm=llm_text, prompt=post_prompt)
headline_chain = LLMChain(llm=llm_text, prompt=headline_prompt)

# DALL·E генерация изображений
# Инициируем генератор с явными параметрами (model, число и размер изображений)
dalle = DallEAPIWrapper(
    api_key=config['openai']['api_key'],
    model="dall-e-3",
    size="1024x1024"
)

class PublishingAgent:
    """Agent для публикации постов в Telegram и уведомлений владельца."""

    async def execute(self):
        logger.info("Start publishing cycle")
        idea_data = sheets_tool.get_next_idea()
        if not idea_data:
            logger.info("No ideas to process.")
            return

        row = idea_data['row']
        idea = idea_data['idea']
        examples = idea_data.get('examples', '')

        # 1) Генерация текста и фактчекинг
        draft_text = post_chain.run({'idea': idea, 'examples': examples})
        checked_text = fact_checker.run(draft_text)

        # 2) Генерация заголовка
        headline = headline_chain.run({'text': checked_text})

        # 3) Генерация изображения
        #image_prompt = f"Иллюстрация для телеграм-поста на тему «{headline}»"
        image_prompt = image_post
        try:
            photo_url = dalle.run(image_prompt)
            logger.info("Image generated: %s", photo_url)
        except Exception as e:
            logger.error("Error generating image: %s", e)
            photo_url = None

        # 4) Публикация в Telegram
        try:
            combined_caption = f"*{headline}*\n\n{checked_text}"
            text_msg = await telegram_tool.send_photo(
                CHANNEL_ID,
                photo_url,
                caption=combined_caption
            )
            logger.info("Published title, image and text to Telegram channel")
        except Exception as e:
            logger.error("Error publishing to Telegram: %s", e)
            return

        # 5) Обновление Google Sheets и память
        sheets_tool.mark_done(row)
        logger.info("Marked idea as done in Google Sheets")

        memory_store.add_document(text=checked_text, metadata={'row': row, 'headline': headline})
        logger.info("Saved publication to memory")

        # 6) Уведомление владельца
        post_link = f"https://t.me/{CHANNEL_USERNAME}/{text_msg.message_id}"
        sent_at = datetime.fromtimestamp(text_msg.date.timestamp()).strftime('%Y-%m-%d %H:%M')
        notification = (
            f"✅ Задание выполнено:\n"
            f"• Канал: @{CHANNEL_USERNAME}\n"
            f"• Заголовок: «{headline}»\n"
            f"• Время: {sent_at}\n"
            f"• Ссылка: {post_link}"
        )
        await telegram_tool.send_message(OWNER_CHAT_ID, notification)
        logger.info("Owner notification sent")

async def main():
    agent = PublishingAgent()

    # Настройка планировщика с timezone из pytz
    tz_name = config.get('scheduling', {}).get('timezone')
    try:
        tz = pytz.timezone(tz_name) if tz_name else None
    except Exception:
        logger.warning("Invalid timezone '%s', using local timezone.", tz_name)
        tz = None

    scheduler = AsyncIOScheduler(timezone=tz)
    for job in config.get('scheduling', {}).get('jobs', []):
        cron_parts = job['cron'].split()
        scheduler.add_job(
            agent.execute,
            trigger='cron',
            timezone=tz,
            minute=cron_parts[0],
            hour=cron_parts[1],
            day='*' if cron_parts[2] == '*' else cron_parts[2],
            month='*' if cron_parts[3] == '*' else cron_parts[3],
            day_of_week=cron_parts[4]
        )
        logger.info("Scheduled job with cron %s", job['cron'])

    scheduler.start()
    logger.info("Scheduler started, running...")
    await asyncio.Event().wait()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down")
