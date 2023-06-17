import sqlite3
import telebot
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler
from telegram.ext import filters
from telegram.ext import Updater

conn = sqlite3.connect('gifts.db')
cursor = conn.cursor()

def start(update, context):
    update.message.reply_text('Привет! Я могу помочь тебе выбрать подарок. Напиши что-нибудь!')

def analyze(update, context):
    chat_html = update.message.reply_to_message.text
    interests = analyze_chat(chat_html)

    # выбираем подарки, соответствующие интересам пользователя
    gifts = []
    for interest in interests:
        cursor.execute("SELECT * FROM gifts WHERE description LIKE ? OR name LIKE ?", ('%' + interest + '%', '%' + interest + '%'))
        gifts.extend(cursor.fetchall())
        if not gifts:
            update.message.reply_text('К сожалению, я не нашел подходящих подарков. Попробуйте еще раз или обратитесь к другому боту.')

    # отправляем пользователю список подарков
    keyboard = [[InlineKeyboardButton("Одобрить", callback_data='approve'),
                 InlineKeyboardButton("Не одобрить", callback_data='disapprove')]]

    for gift in gifts:
        gift_name = gift[1]
        gift_description = gift[2]
        gift_price = gift[3]
        gift_link = gift[4]

        message = f'{gift_name}\n{gift_description}\nЦена: {gift_price} руб.\nСсылка: {gift_link}'
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(message, reply_markup=reply_markup)

def file_handler(update, context):
    file_id = update.message.document.file_id
    file = context.bot.get_file(file_id)
    chat_html = file.download_as_bytearray().decode()
    interests = analyze_chat(chat_html)

    # выбираем подарки соответствующие интересам пользователя
    gifts = []
    for interest in interests:
        cursor.execute("SELECT * FROM gifts WHERE description LIKE ? OR name LIKE ?", ('%' + interest + '%', '%' + interest + '%'))
        gifts.extend(cursor.fetchall())
        if not gifts:
            update.message.reply_text('К сожалению, я не нашел подходящих подарков. Попробуйте еще раз или обратитесь к другому боту.')

    # отправляем пользователю список подарков
    keyboard = [[InlineKeyboardButton("Одобрить", callback_data='approve'),
                 InlineKeyboardButton("Не одобрить", callback_data='disapprove')]]

    for gift in gifts:
        gift_name = gift[1]
        gift_description = gift[2]
        gift_price = gift[3]
        gift_link = gift[4]

        message = f'{gift_name}\n{gift_description}\nЦена: {gift_price} руб.\nСсылка: {gift_link}'
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(message, reply_markup=reply_markup)

def button_handler(update, context):
    query = update.callback_query
    if query.data == 'approve':
        query.answer()
        query.edit_message_text(text="Спасибо! Мы рады, что смогли помочь вам выбрать подарок.")
    elif query.data == 'disapprove':
        query.answer()
        query.edit_message_text(text="Очень жаль! Попробуем еще раз?")

def main():
    token = '5902029822:AAHo54mlJxyjzHqokxOPekkAifeUmwyUJGQ'
    bot = telebot.TeleBot(token)
    updater = Updater(bot=bot, use_context=True)


    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.reply_to_message & Filters.regex('<.*>'), analyze))
    dp.add_handler(MessageHandler(Filters.document.category("text"), file_handler))
    dp.add_handler(CallbackQueryHandler(button_handler))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
