import telebot
import os
from dotenv import load_dotenv
from telebot import types
import json
from transformers import pipeline


load_dotenv()

bot = telebot.TeleBot(os.getenv("TOKEN"))


# Импортируйте модель и токенизатор
qa_pipeline = pipeline("question-answering", model="timpal0l/mdeberta-v3-base-squad2")

# Тестовые данные
try:
    with open('context_0000001.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
except FileNotFoundError:
    pass

context = "\n".join(data)
print(context)


question_answering = "question_answering.json"


def save_question_answering(user_id, text, result):
    try:
        with open(question_answering, 'r', encoding='utf-8') as file:
            qa = json.load(file)
    except FileNotFoundError:
        qa = {"qa_pairs": []}
    qa_pair = {"user_id": user_id, "question": text, "answer": result['answer']}
    qa["qa_pairs"].append(qa_pair)
    with open(question_answering, 'w', encoding='utf-8') as file:
        json.dump(qa, file, ensure_ascii=False, indent=4)


qa_review = "qa_review.json"


def save_qa_review(user_id, message_id, review):
    try:
        with open(qa_review, 'r', encoding='utf-8') as file:
            qa = json.load(file)
    except FileNotFoundError:
        qa = {"qa_pairs": []}
    qa_pair = {"user_id": user_id, "message_id": message_id, "review": review}
    qa["qa_pairs"].append(qa_pair)
    with open(qa_review, 'w', encoding='utf-8') as file:
        json.dump(qa, file, ensure_ascii=False, indent=4)


# Create a dictionary to keep track of the user's state
user_state = {}


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Я согласен(-на) ✅', callback_data='ask')
    markup.add(btn1)
    bot.send_message(message.from_user.id, "Данный бот находится на этапе разработки!\n"
                                           "Для улучшения качества сервиса происходит сбор данных, "
                                           "для продолжения нужно Ваше согласие", reply_markup=markup)


# Handle the "Я согласен" button click event
@bot.message_handler(func=lambda message: message.text == 'Задать еще вопрос ✏️')
@bot.callback_query_handler(func=lambda call: call.data == 'ask')
def ask_question(message):
    user_id = message.from_user.id
    user_state[user_id] = 'waiting_for_question'
    bot.send_message(user_id, "Что вы хотите узнать?", reply_markup=clear_keyboard())


# Handle text messages
@bot.message_handler(func=lambda message: user_state.get(message.from_user.id) == 'waiting_for_question')
def handle_question(message):
    user_id = message.from_user.id
    user_state.pop(user_id, None)  # Clear the user's state
    print(f"Пользователь спросил: {message.text}")
    result = qa_pipeline(question=message.text, context=context)
    print(f"Бот ответил: {result['answer']}")

    save_question_answering(user_id, message.text, result)
    bot.send_message(user_id, f"Ответ: {result['answer']}", reply_markup=create_new_question_button())

    bot.send_message(user_id, "Поставьте оценку ответу:", reply_markup=review_inline_button())


# Create the "Задать еще вопрос" button
def create_new_question_button():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    new_question_button = types.KeyboardButton(text="Задать еще вопрос ✏️")
    markup.add(new_question_button)
    return markup


def clear_keyboard():
    markup = telebot.types.ReplyKeyboardRemove()
    return markup


def review_inline_button():
    markup = types.InlineKeyboardMarkup()
    positively = types.InlineKeyboardButton(text='Хороший ответ✅', callback_data='positively')
    negative = types.InlineKeyboardButton(text='Плохой ответ❌', callback_data='negative')
    markup.add(positively)
    markup.add(negative)

    return markup


@bot.callback_query_handler(func=lambda call: call.data == 'positively')
@bot.callback_query_handler(func=lambda call: call.data == 'negative')
def print_save_review(call):
    user_id = call.from_user.id
    message_id = call.message.message_id
    # Определите, какой вариант (положительный или отрицательный) был выбран
    if call.data == 'positively':
        # Пользователь отметил ответ как хороший
        bot.send_message(user_id, "Спасибо за вашу оценку! Ответ отмечен как хороший. Мы ценим вашу обратную связь.")
    elif call.data == 'negative':
        # Пользователь отметил ответ как плохой
        bot.send_message(user_id, "Спасибо за вашу оценку! Ответ отмечен как плохой. Мы ценим вашу обратную связь.")

    # Сохраните вопрос и ответ в JSON-файл
    save_qa_review(user_id, message_id, call.data)

    # Удалите инлайн-клавиатуру после оценки
    bot.edit_message_reply_markup(user_id, message_id, reply_markup=None)


print("Bot is running!")
bot.polling(none_stop=True, interval=0)
