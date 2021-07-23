from telebot import *
from multiprocessing import *
import schedule
from downloader import update_file
from pdf_parser import check_new_students
from pickle import load, dump
from logger import logging

token = '' # Токен
bot = telebot.TeleBot(token)
users = set ()  # Список пользователей, подписанных на уведомления
faculty = 'ИУ7' # Название отслеживаемого факультета
frequency = 20 * 60 # Частота запросов (секунды)

def create_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    download_btn = types.InlineKeyboardButton(text="Скачать полный список", callback_data="download")
    list_iu7_btn = types.InlineKeyboardButton(text="Список людей зарегистрированных на {}".format(faculty), callback_data="list_reg")
    count_iu7_btn = types.InlineKeyboardButton(text="Количество зарегистрированных на {}".format(faculty), callback_data="count_reg")
    
    keyboard.add(download_btn)
    keyboard.add(list_iu7_btn)
    keyboard.add(count_iu7_btn)

    return keyboard

def start_process():
    p1 = Process(target=P_schedule.start_schedule, args=()).start()
 
class P_schedule():
    def start_schedule():
        schedule.every(frequency).seconds.do(P_schedule.check_students)

        while True:
            schedule.run_pending()
            time.sleep(1)

    def check_students():
        with open('tmp/users', 'rb') as f:
            users = load(f)
        new_students = check_new_students(faculty)
        if new_students == '':
            logging.info("new students not found")
        else:
            logging.info("new students found")
            for i in users:
                bot.send_message(i, 'Новые абитуриенты:\n'+new_students)
            logging.info("notifications have been sent out successfully")


@bot.message_handler(commands=['start'])
def start_bot(message):
    keyboard = create_keyboard()

    users.add(message.chat.id)
    with open('tmp/users', 'wb') as f:
        dump(users, f)
    logging.info("the user [{}] was added to users set".format(message.chat.id))
    bot.send_message(
        message.chat.id,
        "Привет! Данный бот поможет вам не упустить из виду ни одного абитуринта ;)")
    bot.send_message(
        message.chat.id,
        "Вы автоматически подписаны на рассылку уведомлений о новых абитуриентов! Если вы хотите отказаться от рассылки введите команду [/cancel].",
        reply_markup=keyboard
    )


@bot.message_handler(commands=['update'])
def update_data(message):
    P_schedule.check_students()
    bot.send_message(message.chat.id,
    "Данные принудительно обновлены!")


@bot.message_handler(commands=['cancel'])
def cancel_notification(message):
    with open('tmp/users', 'rb') as f:
        users_set = load(f)
    if (message.chat.id in users_set):
        users_set.remove(message.chat.id)
        with open('tmp/users', 'wb') as f:
            dump(users_set, f)
        bot.send_message(message.chat.id, "Вы успешно отменили подписку на уведомления! Для возобновления введите команду [/subscribe].")
        logging.info("user [{}] canceled notifications".format(message.chat.id))
    else:
        bot.send_message(message.chat.id, "Ваша подписка на уведомления не активирована! Для возобновления введите команду [/subscribe].")


@bot.message_handler(commands=['subscribe'])
def cancel_notification(message):
    with open('tmp/users', 'rb') as f:
        users_set = load(f)
    if (message.chat.id not in users_set):
        users_set.add(message.chat.id)
        with open('tmp/users', 'wb') as f:
            dump(users_set, f)
        bot.send_message(message.chat.id, "Вы успешно оформили подписку на уведомления! Для отмены введите команду [/cancel].")
        logging.info("user [{}] subscribed to notifications".format(message.chat.id))
    else:
        bot.send_message(message.chat.id, "Ваша подписка на уведомления уже активирована! Для отмены введите команду [/cancel].")


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    keyboard = create_keyboard()
    if call.message:
        if call.data == "download":
            file_path = update_file()
            with open(file_path, 'rb') as f:
              bot.send_document(call.message.chat.id, f, reply_markup=keyboard)
            logging.info("user [{}] downloaded file".format(call.message.chat.id))
        
        elif call.data == "list_reg":
            with open('tmp/students_faculty', 'rb') as f:
                list_data = load(f)
            bot.send_message(call.message.chat.id, list_data[0], reply_markup=keyboard) 
            logging.info("user [{}] printed registration list".format(call.message.chat.id))

        
        elif call.data == "count_reg":
            with open('tmp/students_faculty', 'rb') as f:
                list_data = load(f)
            bot.send_message(call.message.chat.id, "На направление {} зарегистрировано всего: {}\nНа платной основе: {}\nЦелевое обучение: {}\nНа бюджетной основе: {}".format(faculty, list_data[1],list_data[2], list_data[3], list_data[1] - list_data[2] - list_data[3]), reply_markup=keyboard)
            logging.info("user [{}] printed count".format(call.message.chat.id))


if __name__ == '__main__':
    start_process()
    try:
        bot.polling(none_stop=True)
    except:
        logging.error("bot.polling is not avaible!")
