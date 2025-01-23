import logging
import os
from dotenv import load_dotenv
# from telegram import Update
# from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
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
    if update.message:  # Проверка на наличие пользовательского ввода
        update.message.reply_text('Привет! Я бот, как я могу помочь?')
    else:
        update.message.reply_text("Необходимо ввести сообщение.")

# Генерация текста с использованием модели
def generate_text(update: Update, context: CallbackContext) -> None:
    if update.message and nlp_model:  # Проверка на наличие пользовательского ввода и модели
        try:
            user_input = update.message.text
            generated = nlp_model(user_input, max_length=50, num_return_sequences=1)
            update.message.reply_text(generated[0]['generated_text'])
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            update.message.reply_text("Произошла ошибка при обработке запроса.")
    else:
        update.message.reply_text("Необходимо ввести сообщение.")

def main():
    # Проверка на наличие файла bot.py
    if os.path.exists("bot.py"):
        # Проверка на наличие файла .env
        if os.path.exists(".env"):
            # Проверка на наличие токена Telegram
            token = os.getenv("TELEGRAM_API_TOKEN")
            if token:
                # Проверка на наличие модели
                if nlp_model:
                    # Запуск бота
                    updater = Updater(token, use_context=True)
                    dispatcher = updater.dispatcher

                    # Обработчики команд
                    dispatcher.add_handler(CommandHandler("start", start))

                    # Обработчик текста
                    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, generate_text))

                    # Запуск бота
                    updater.start_polling()
                    updater.idle()
                else:
                    logger.error("Модель не доступна.")
            else:
                logger.error("Токен Telegram не найден.")
        else:
            logger.error(".env файл не найден.")
    else:
        logger.error("bot.py файл не найден.")

if __name__ == '__main__':
    main()