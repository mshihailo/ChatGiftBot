import telegram
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters
import openai
from enum import Enum

openai.api_key = "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"

class ConversationState(Enum):
    START = 1
    ASK_AGE = 2
    ASK_GENDER = 3
    ASK_HOBBY = 4
    ASK_PROFESSION = 5
    ASK_BUDGET = 6
    ASK_EVENT = 7
    ASK_CUSTOM_EVENT = 8  # Добавлено для возможности ввода пользовательского события
    ASK_SATISFIED = 9


def start(update: Update, context: CallbackContext):
    # Инициализируем состояние беседы
    context.user_data['state'] = ConversationState.ASK_AGE
    update.message.reply_text('Привет! Я твой личный помощник на все праздники. Я могу помочь тебе подобрать подарок для твоих близких.\n\nДля получения списка команд введите /help')

   # Добавляем кнопку "Завершить поиск"
    reply_keyboard = [[KeyboardButton('/stop')]] 
    update.message.reply_text('Начнём! Необходимо ввести данные про получателя подарка. Начнём с возраста:', reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))


def help_command(update: Update, context: CallbackContext):
    text = 'Список доступных команд:\n\n'
    text += '/start - начать поиск подарка\n'
    text += '/help - вывести список доступных команд\n'
    text += '/stop - завершить поиск подарка и закончить диалог\n'
    update.message.reply_text(text)


def stop_command(update: Update, context: CallbackContext):
    update.message.reply_text('Спасибо за использование нашего сервиса! Желаем хорошо провести время вместе с близкими.')
    context.user_data.clear()


def echo(update: Update, context: CallbackContext):
    # Получаем текущее состояние беседы
    state = context.user_data.get('state', ConversationState.START)

    if state == ConversationState.ASK_AGE:
        try:
            age = int(update.message.text)
            context.user_data['age'] = age
            context.user_data['state'] = ConversationState.ASK_GENDER

            # Добавляем кнопку "Завершить поиск"
            reply_keyboard = [[KeyboardButton('/stop')]]
            # Добавляем кнопки "Мужской" и "Женский"
            reply_keyboard = [[KeyboardButton('Мужской'), KeyboardButton('Женский')]]
            update.message.reply_text('Введите пол:', reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))
            
        except ValueError:
            update.message.reply_text('Неверный формат ввода. Пожалуйста, введите возраст цифрами.')
    
    elif state == ConversationState.ASK_GENDER:
        gender = update.message.text
        context.user_data['gender'] = gender
        context.user_data['state'] = ConversationState.ASK_HOBBY
        # Добавляем кнопку "Завершить поиск"
        reply_keyboard = [[KeyboardButton('/stop')]]
        # Добавляем кнопку "Пропустить" для возможности пропустить ввод хобби/интересов
        reply_keyboard = [[KeyboardButton('Пропустить')]]
        update.message.reply_text('Введите хобби/интересы через запятую или нажмите кнопку "Пропустить":', reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))
        
    elif state == ConversationState.ASK_HOBBY:
        hobby = update.message.text
        context.user_data['hobby'] = hobby
        context.user_data['state'] = ConversationState.ASK_PROFESSION
        # Добавляем кнопку "Завершить поиск"
        reply_keyboard = [[KeyboardButton('/stop')]]
        # Добавляем кнопку "Пропустить" для возможности пропустить ввод рода деятельности
        reply_keyboard = [[KeyboardButton('Пропустить')]]
        update.message.reply_text('Введите род деятельности или нажмите кнопку "Пропустить":', reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))
        
    elif state == ConversationState.ASK_PROFESSION:
        profession = update.message.text
        context.user_data['profession'] = profession
        context.user_data['state'] = ConversationState.ASK_BUDGET
    # Добавляем кнопку "Завершить поиск"
        reply_keyboard = [[KeyboardButton('/stop')]]
        # Добавляем кнопку "Пропустить" для возможности пропустить ввод бюджета
        reply_keyboard = [[KeyboardButton('Пропустить')]]
        update.message.reply_text('Введите бюджет в рублях или нажмите кнопку "Пропустить":', reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))

    elif state == ConversationState.ASK_BUDGET:
        try:
            budget = int(update.message.text)
            context.user_data['budget'] = budget
            context.user_data['state'] = ConversationState.ASK_EVENT
        # Добавляем кнопку "Завершить поиск"
            reply_keyboard = [[KeyboardButton('/stop')]]
        # Добавляем кнопки для выбора события (Новый год, День рождения и т.д.)
            reply_keyboard = [
                [KeyboardButton('Новый год'), KeyboardButton('День рождения')],
                [KeyboardButton('Именины'), KeyboardButton('Рождество')],
                [KeyboardButton('Годовщина'), KeyboardButton('14 февраля')],
                [KeyboardButton('Другое')]
                ]
            update.message.reply_text('Выберите событие:', reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))
        except ValueError:
            update.message.reply_text('Неверный формат ввода. Пожалуйста, введите бюджет цифрами.')

    elif state == ConversationState.ASK_EVENT:
        event = update.message.text.lower()
        if event == 'другое':
            context.user_data['state'] = ConversationState.ASK_CUSTOM_EVENT
            update.message.reply_text('Введите название события:')
        else:
            suggest_gifts(update, context, event)
        
    elif state == ConversationState.ASK_CUSTOM_EVENT:
        custom_event = update.message.text.lower()
        suggest_gifts(update, context, custom_event)
    
    elif state == ConversationState.ASK_SATISFIED:
        if 'да' in update.message.text.lower():
            event = context.user_data['event']
            update.message.reply_text(f'Желаем вам хорошо провести {event}!')
            context.user_data.clear()
        else:
            suggest_gifts(update, context, context.user_data['event'])

def suggest_gifts(update: Update, context: CallbackContext, event: str):
    age = context.user_data.get('age', '')
    gender = context.user_data.get('gender', '')
    hobby = context.user_data.get('hobby', '')
    profession = context.user_data.get('profession', '')
    budget = context.user_data.get('budget', '')

    prompt = f"Подобрать подарок и сформировать список для человека {gender} пола, {age} лет, увлекающегося {hobby}, занимающегося {profession}. Бюджет - {budget} рублей. Событие - {event}."
    response = openai.Completion.create(model='text-davinci-002', prompt=prompt, max_tokens=500)
    gift_recommendation = response.choices[0].text
    # Добавляем кнопку "Завершить поиск"
    reply_keyboard = [[KeyboardButton('/stop')]]
    # Добавляем кнопки "Да" и "Нет" для возможности выбора удовлетворительности подарка
    reply_keyboard = [[KeyboardButton('Да'), KeyboardButton('Нет')]]
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Предлагаю следующие варианты подарков:\n\n{gift_recommendation}\n\nНашли, что искали?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))

    context.user_data['event'] = event
    context.user_data['state'] = ConversationState.ASK_SATISFIED

def error(update: Update, context: CallbackContext):
    print(f'Update {update} caused error {context.error}')

#Добавление обработчиков
updater = Updater(token='5902029822:AAHo54mlJxyjzHqokxOPekkAifeUmwyUJGQ', use_context=True)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help_command))
updater.dispatcher.add_handler(CommandHandler('stop', stop_command))
updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
updater.dispatcher.add_error_handler(error)

#Запуск бота
updater.start_polling()
updater.idle()

