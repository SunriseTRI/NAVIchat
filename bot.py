import os
from bs4 import BeautifulSoup
import telebot
from datasets import load_dataset

ds = load_dataset("gretelai/synthetic_text_to_sql")

# Инициализация бота
API_TOKEN = '7689394185:AAEWM3CROdX36aFGyGDHjqkdthQQAzT-i3w'
bot = telebot.TeleBot(API_TOKEN)

# ID администратора
ADMIN_USER_ID = "@raringfern"  # замените на свой ID
from transformers import pipeline

# Подключаем модель для генерации текста
nlp_model = pipeline("text-generation", model="gpt-2")

def get_answer_from_model(question):
    # Генерация ответа от модели
    response = nlp_model(question, max_length=100)
    return response[0]['generated_text']


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    username = message.from_user.username
    user = get_user_by_username(username)  # Проверка, есть ли пользователь в базе данных

    if not user:
        bot.reply_to(message, "Пожалуйста, зарегистрируйтесь с помощью команды /reg")
        return

    rows = get_faq()  # Получаем все вопросы из FAQ
    exact_answer = next((row[1] for row in rows if row[0].lower() in message.text.lower()), None)

    if exact_answer:
        bot.reply_to(message, exact_answer)
    else:
        answer = get_answer_from_model(message.text)
        if not answer or "[CLS]" in answer:
            bot.reply_to(message, "Не могу ответить на этот вопрос, он добавлен для дальнейшей обработки.")
            insert_unanswered_question(message.text, username)  # Сохранение нерешённого вопроса
        else:
            bot.reply_to(message, answer)


import sqlite3

def create_db():
    conn = sqlite3.connect('chat_bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, name TEXT, surname TEXT, age INTEGER, phone TEXT, email TEXT, user_type TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY, user_id INTEGER, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS unanswered_questions
                 (id INTEGER PRIMARY KEY, question TEXT, user_id INTEGER)''')
    conn.commit()
    conn.close()
def import_chat_messages(file_path):
    if not os.path.exists(file_path):
        return "Файл не найден!"

    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
        messages = soup.find_all("div", class_="message")

        for message in messages:
            text = message.get_text(strip=True)
            user = message.find("span", class_="user").get_text(strip=True)
            save_chat_message(user, text)

    return "Чат успешно импортирован!"

# Команда импорта чатов для администраторов
@bot.message_handler(commands=['import_chat'])
def import_chat(message):
    # Проверяем, является ли пользователь администратором
    if message.from_user.id != ADMIN_USER_ID:
        bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
        return

    # Путь к файлу для импорта
    file_path = 'exported/ChatExport_2025-01-17/messages.html'
    result = import_chat_messages(file_path)
    bot.reply_to(message, result)

# Функция обработки всех сообщений
@bot.message_handler(func=lambda message: True)
def handle_user_message(message):
    username = message.from_user.username
    user = get_user_by_username(username)

    if not user:
        bot.reply_to(message, "Пожалуйста, зарегистрируйтесь, используя команду /reg.")
        return

    if user['user_type'] == 'admin':
        bot.reply_to(message, "Привет, админ! Чем могу помочь?")
    else:
        bot.reply_to(message, "Я занят, идите на хрен!")

def insert_unanswered_question(question, username):
    conn = sqlite3.connect('chat_bot.db')
    c = conn.cursor()
    c.execute("INSERT INTO unanswered_questions (question, user_id) VALUES (?, ?)", (question, username))
    conn.commit()
    conn.close()



# Запуск бота
if __name__ == "__main__":
    bot.polling(none_stop=True)
