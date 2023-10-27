import telebot
import os
from dotenv import load_dotenv
from telebot import types

load_dotenv()

bot = telebot.TeleBot(os.getenv("TOKEN"))

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
    bot.send_message(user_id, f"Вы хотите узнать: {message.text}", reply_markup=create_new_question_button())


# Create the "Задать еще вопрос" button
def create_new_question_button():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    new_question_button = types.KeyboardButton(text="Задать еще вопрос ✏️")
    markup.add(new_question_button)
    return markup


def clear_keyboard():
    markup = telebot.types.ReplyKeyboardRemove()
    return markup


print("Bot is running!")
bot.polling(none_stop=True, interval=0)
