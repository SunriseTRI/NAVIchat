import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from transformers import pipeline

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка модели
try:
    nlp_model = pipeline("text-generation", model="gpt-2")
    logger.info("Model loaded successfully.")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    nlp_model = None

# Команда start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Я бот, как я могу помочь?')

# Генерация текста с использованием модели
def generate_text(update: Update, context: CallbackContext) -> None:
    if nlp_model:
        try:
            user_input = update.message.text
            generated = nlp_model(user_input, max_length=50, num_return_sequences=1)
            update.message.reply_text(generated[0]['generated_text'])
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            update.message.reply_text("Произошла ошибка при обработке запроса.")
    else:
        update.message.reply_text("Модель не доступна.")

def main():
    # Получение токена из переменных окружения
    token = os.getenv("TELEGRAM_API_TOKEN")
    if not token:
        logger.error("Telegram token not found!")
        return

    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher

    # Обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))

    # Обработчик текста
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, generate_text))

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
