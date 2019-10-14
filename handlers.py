import os
import re
from glob import glob
from random import choice

import ephem
from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, ParseMode, error, InlineKeyboardButton, \
    InlineKeyboardMarkup
from telegram.ext import ConversationHandler, messagequeue as mq

from db import get_or_create_user, db, toggle_subscription, get_subscribed
from translator import translator
from utils import is_cat, keyboard
from datetime import datetime


# subscribers = set()


def check_user_photo(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    update.message.reply_text("Обрабатываю фото")
    os.makedirs('downloads', exist_ok=True)
    photo_file = bot.getFile(update.message.photo[-1].file_id)
    filename = os.path.join('downloads', '{}.jpg'.format(photo_file.file_id))
    photo_file.download(filename)
    # update.message.reply_text("Файл сохранен")
    if is_cat(filename):
        update.message.reply_text("Обнаружен men, добавляю в библиотеку.")
        new_filename = os.path.join('images', '{}.jpg'.format(photo_file.file_id))
        os.rename(filename, new_filename)
    else:
        os.remove(filename)
        update.message.reply_text("Тревога, котик не обнаружен!")


def anketa_start(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    update.message.reply_text("Как вас зовут? Напишите имя и фамилию", reply_markup=ReplyKeyboardRemove())
    return "name"


def anketa_get_name(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    user_name = update.message.text
    if len(user_name.split(" ")) < 2:
        update.message.reply_text("Пожалуйста, напишите имя и фамилию")
        return "name"
    else:
        user_data["anketa_name"] = user_name
        reply_keyboard = [["1", "2", "3", "4", "5"]]

        update.message.reply_text(
            "Оцените бота по шкале от 1 до 5",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return "rating"


def anketa_rating(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    user_data["anketa_rating"] = update.message.text

    update.message.reply_text("""Оставьте комментарий в свободной форме 
        или пропустите этот шаг, введя /skip""")
    return "comment"


def anketa_comment(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    user_data["anketa_comment"] = update.message.text
    user_text = """
<b>Имя Фамилия:</b> {anketa_name}
<b>Оценка:</b> {anketa_rating}
<b>Комментарий:</b> {anketa_comment}""".format(**user_data)

    update.message.reply_text(user_text, reply_markup=keyboard(),
                              parse_mode=ParseMode.HTML)
    return ConversationHandler.END


def anketa_skip_comment(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    text = """
<b>Имя Фамилия:</b> {anketa_name}
<b>Оценка:</b> {anketa_rating}""".format(**user_data)

    update.message.reply_text(text, reply_markup=keyboard(),
                              parse_mode=ParseMode.HTML)
    return ConversationHandler.END


def dontknow(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    update.message.reply_text("Не понимаю")


def subscribe(bot, update):
    user = get_or_create_user(db, update.effective_user, update.message)
    if not user.get('subscribed'):
        toggle_subscription(db, user)
    update.message.reply_text('Вы подписались /unsubscribe чтобы отписаться')


@mq.queuedmessage
def send_updates(bot, job):
    for user in get_subscribed(db):
        try:
            bot.sendMessage(chat_id=user['chat_id'], text="BUZZZ!")
        except error.BadRequest:
            print('Chat {} not found'.format(user['chat_id']))


@mq.queuedmessage
def alarm(bot, job):
    bot.send_message(chat_id=job.context, text="Сработал будильник!")


def unsubscribe(bot, update):
    user = get_or_create_user(db, update.effective_user, update.message)
    if user.get('subscribed'):
        toggle_subscription(db, user)
        update.message.reply_text("Вы отписались")
    else:
        update.message.reply_text("Вы не подписаны, нажмите /subscribe чтобы подписаться")


def set_alarm(bot, update, args, job_queue):
    user = get_or_create_user(db, update.effective_user, update.message)
    try:
        seconds = abs(int(args[0]))
        job_queue.run_once(alarm, seconds, context=update.message.chat_id)
    except (IndexError, ValueError):
        update.message.reply_text("Введите число секунд после команды /alarm")


def inline_button_pressed(bot, update):
    query = update.callback_query
    if query.data in ['cat_good', 'cat_bad']:
        text = "Круто" if query.data == "cat_good" else "Печаль"

        bot.edit_message_caption(caption=text, chat_id=query.message.chat_id,
                                 message_id=query.message.message_id)


def send_picture(bot, update):
    user = get_or_create_user(db, update.effective_user, update.message)
    img_list = glob('images/*.jpg')
    pic = choice(img_list)
    inlinekbd = [[InlineKeyboardButton(":thumbs_up:", callback_data='cat_good'),
                  InlineKeyboardButton(":thumbs_down:", callback_data='cat_bad')]]

    kbd_markup = InlineKeyboardMarkup(inlinekbd)
    bot.send_photo(chat_id=update.message.chat.id, photo=open(pic, 'rb'), reply_markup=kbd_markup)


def planet(bot, update, args):
    try:
        planet_name = translator(args[0].capitalize())
        try:
            today = datetime.now(tz=None).strftime('%Y/%m/%d')
            # planet = eval("ephem." + st)(today)
            planet = getattr(ephem, planet_name)(today)
            return update.message.reply_text(ephem.constellation(planet))

        except AttributeError:
            return update.message.reply_text("Нет такой планеты")

    except (IndexError, ValueError):
        update.message.reply_text("Введите название планты после /planet")


def next_full_moon(bot, update, args):
    try:
        date = args[0]
        update.message.reply_text(ephem.next_full_moon(date))
    except (IndexError, ValueError):
        update.message.reply_text("Введите дату в формате гггг-мм-дд после /full_moon")


def calculator(bot, update, args):
    try:
        expression = args[0]
        try:
            match = re.fullmatch('[-+]?\d([-+/*]?\d)+', expression)
            a = expression if match else "'Неверный ввод'"
            return update.message.reply_text(eval(a))
        except ZeroDivisionError:
            return update.message.reply_text("Деление на ноль")
    except (IndexError, ValueError):
        update.message.reply_text("Введите арифметическое выражение после /calc")


def wordcount(bot, update, args):
    try:
        text = args
        update.message.reply_text(f"Количество слов: {len(text)}")
    except (IndexError, ValueError):
        update.message.reply_text("Введите предложение после /wordcount")
