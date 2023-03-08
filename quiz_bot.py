import telebot
import re
import random
import uuid
from yaml_parser import load_yaml, get_correct
from db_functionality import push_todb
from telebot import types

bot = telebot.TeleBot("<TOKEN>")

user_dict = {}

class User:
    def __init__(self, nick):
        self.nickname = nick
        self.name = None
        self.surname = None
        self.phone = None
        self.questions = None
        self.score = 0

itembtn_quiz = types.KeyboardButton('Play quiz')
itembtn_info = types.KeyboardButton('Info')
itembtn_question = types.KeyboardButton('Ask question')
itembtn_presentations = types.KeyboardButton('Get info about presentations')
default_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True).row(itembtn_quiz, itembtn_info).row(itembtn_question, itembtn_presentations)

hideBoard = types.ReplyKeyboardRemove()

@bot.message_handler(func=lambda message: message.text == "Back" or message.text == "/start")
def welcome(message, chat_id=None):
    if message:
        welcome_msg = 'Welcome to my bot! What do you want?'
        chat_id=message.chat.id
    else:
        welcome_msg = 'Main menu'
    bot.send_message(chat_id, welcome_msg, reply_markup=default_markup)
    

@bot.message_handler(func=lambda message: message.text == "Get info about presentations")
def info(message):
    msg = 'Presentations'
    mesg = bot.send_message(message.chat.id, msg, reply_markup=default_markup)

@bot.message_handler(func=lambda message: message.text == "Info")
def info(message):
    
    # Main menu markup
    itembtn_stand = types.KeyboardButton('Get info about stand')
    itembtn_hours = types.KeyboardButton('Working hours')
    itembtn_speakers = types.KeyboardButton('Get info about speakers')
    itembtn_bar = types.KeyboardButton('Get bar menu')
    itembtn_back = types.KeyboardButton('Back')
    info_markup = types.ReplyKeyboardMarkup().row(itembtn_stand, itembtn_speakers)\
                                             .row(itembtn_bar, itembtn_hours)\
                                             .row(itembtn_back)
                                             
    msg = 'Choose category'
    bot.send_message(message.chat.id, msg, reply_markup=info_markup)

@bot.message_handler(func=lambda message: message.text == "Get info about stand")
def info_stand(message):
    msg = 'Stand Info'
    bot.send_message(message.chat.id, msg, reply_markup=default_markup)

@bot.message_handler(func=lambda message: message.text == "Working hours")
def info_hours(message):
    msg = 'Working hours'
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda message: message.text == "Get info about speakers")
def info_speakers(message):
    msg = 'Speakers list and info'
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda message: message.text == "Get bar menu")
def info_bar(message):
    msg = 'Bar menu'
    bot.send_message(message.chat.id, msg)

def remove_reply_keyboard(message):
    bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id, reply_markup=hideBoard)

# This section deseibes quiz rules
@bot.message_handler(func=lambda message: message.text == "Play quiz")
def quiz_entry(message):
    itembtn_reg = types.InlineKeyboardButton('Register', callback_data="reg")
    itembtn_can = types.InlineKeyboardButton('Cancel',  callback_data="can")
    ph_markup = types.InlineKeyboardMarkup().add(itembtn_reg).add(itembtn_can)
    
    bot.send_message(message.chat.id, "In order to participate in quiz you have to register", reply_markup=ph_markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    chat_id=call.from_user.id
    
    if call.data == "reg":
        bot.send_message(chat_id, text='What is your name?')
        bot.register_next_step_handler(call.message, get_name)
    elif call.data ==  "can":
        welcome(None, chat_id)
            
    #Quiz-triggered cases
    elif call.data ==  get_correct(yml, user_dict[chat_id].questions.pop()):
        item = types.KeyboardButton('Следующий вопрос')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(item)
        user_dict[chat_id].score += 1
        mesg = bot.send_message(chat_id, text='Correct!', reply_markup=markup)
        bot.register_next_step_handler(mesg, quiz_iter)
    else:
        item = types.KeyboardButton('Следующий вопрос')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(item)
        mesg = bot.send_message(chat_id, text='Incorrect', reply_markup=markup)
        bot.register_next_step_handler(mesg, quiz_iter)

def get_name(message):
    try:
        chat_id = message.chat.id
        user = User(message.from_user.username)
        user_dict[chat_id] = user
        name = message.text
        if any(i.isdigit() for i in name):
            msg = bot.reply_to(message, 'Please enter a valid surname')
            bot.register_next_step_handler(msg, get_phone)
            return
        user.name = name
        msg = bot.send_message(chat_id, 'What is your surname?')
        bot.register_next_step_handler(msg, get_surname)
    except Exception as e:
        print(e)
        bot.reply_to(message, 'Error at name completion stage')

def get_surname(message):
    try:
        chat_id = message.chat.id
        surname = message.text
        if any(i.isdigit() for i in surname):
            msg = bot.reply_to(message, 'Please enter a valid surname')
            bot.register_next_step_handler(msg, get_phone)
            return
        user = user_dict[chat_id]
        user.surname = surname 
        msg = bot.send_message(chat_id, 'What is your phone number?')
        bot.register_next_step_handler(msg, get_phone)
    except Exception as e:
        bot.reply_to(message, 'oooops')

def get_phone(message):
    try:
        chat_id = message.chat.id
        phone_regex = re.compile(r'^\+\d{11}$')
        phone = message.text
        if not phone_regex.match(phone):
            msg = bot.reply_to(message, 'Please enter a valid phone number')
            bot.register_next_step_handler(msg, get_phone)
            return
        user = user_dict[chat_id]
        user.phone = phone
        
        itembtn1 = types.KeyboardButton('Confirm')
        itembtn2 = types.KeyboardButton('Rewrite')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add(itembtn1).add(itembtn2)

        profile = f'\
                   Is this profile data correct?:\
                   \nTelegram ID: @{user.nickname}\
                   \nName: {user.name}\
                   \nSurname: {user.surname}\
                   \nPhone: {user.phone}'
        msg = bot.send_message(chat_id, profile, reply_markup=markup)
        bot.register_next_step_handler(msg, quiz_junction)
    except Exception as e:
        print(e)
        bot.reply_to(message, 'oooops')

def quiz_junction(message):
    chat_id = message.chat.id
    if message.text == 'Confirm':
        user = user_dict[chat_id]
        user.questions = random.sample(range(1, 29), 7)
        itemb = types.KeyboardButton('Начинаем!')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(itemb)
        mesg = bot.send_message(message.chat.id, "Регистрация успешна!\nГотовы начать?", reply_markup=markup)
        bot.register_next_step_handler(mesg, quiz_iter)
    elif message.txt == 'Rewrite':
        del user_dict[chat_id]
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Register')
        mesg = bot.send_message(message.chat.id, "Registrating again", reply_markdup=markup)
        bot.register_next_step_handler(mesg, get_name)
    else:
        pass

def quiz_iter(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if user.questions:
        q_id = user.questions[-1]
        option1 = types.InlineKeyboardButton('A', callback_data='a')
        option2 = types.InlineKeyboardButton('B', callback_data='b')
        option3 = types.InlineKeyboardButton('C', callback_data='c')
        option4 = types.InlineKeyboardButton('D', callback_data='d')
        keyboard = types.InlineKeyboardMarkup().add(option1)
        keyboard.add(option2)
        keyboard.add(option3)
        keyboard.add(option4)

        q = yml[q_id-1]['q']
        a1, a2, a3, a4 = yml[q_id-1]['a'][0], yml[q_id-1]['a'][1], yml[q_id-1]['a'][2], yml[q_id-1]['a'][3]

        question = f'{q}\n\
                     \nA) {a1}\
                     \n\nB) {a2}\
                     \n\nC) {a3}\
                     \n\nD) {a4}'
        
        bot.send_message(message.chat.id, question, reply_markup=keyboard)
    else:
        itembtn_back = types.KeyboardButton('Back')
        return_markup = types.ReplyKeyboardMarkup().add(itembtn_back)

        push_todb(user)
        
        if user.score > 4:
            bot.send_message(message.chat.id, f"You've passed!\nScore: {user.score}/7\nYour Promocode: {uuid.uuid4()}", reply_markup=return_markup)
        else:
            bot.send_message(message.chat.id, f"You didn't score enough\nScore: {user.score}/7", reply_markup=return_markup)
        
        welcome(None, chat_id)

def handle_answer(mes):
    pass

yml = load_yaml()
bot.infinity_polling()
