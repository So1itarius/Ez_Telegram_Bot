import logging
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler, RegexHandler, \
    messagequeue as mq, CallbackQueryHandler

from db import get_or_create_user, db
from handlers import check_user_photo, anketa_start, anketa_get_name, anketa_rating, anketa_comment, \
    anketa_skip_comment, dontknow, subscribe, send_updates, unsubscribe, set_alarm, inline_button_pressed, send_picture, \
    next_full_moon, wordcount, calculator, planet
from minigame import new_cities_list, game_dict, start_game
from settings import TOKEN_FOR_BOT


from utils import keyboard

update_id = None
ORIG_CITIES = new_cities_list()


def my_test(bot, job):
    pass
    # bot.sendMessage(chat_id=144091076, text="Lovely Spam! Wonderful Spam!")
    # job.interval += 5
    # if job.interval > 20:
    #    bot.sendMessage(chat_id=144091076, text="Пока!")
    #    job.schedule_removal()


def start(bot, update):
    """Send a message when the command /start is issued."""
    # print(update.message)
    user = get_or_create_user(db, update.effective_user, update.message)
    # print(user)
    text = 'Вызван /start, ВНИМАНИЕ БОТ НЕ ЗАСТРАХОВАН ОТ ВВОДА ВСЯКОЙ ХУЙНИ!'

    game_dict[
        update.message.chat.id] = ORIG_CITIES.copy()  # Формируем словарь с городами в момент начала пользования чатом,
    # используя заранее заготовленный оригинал

    update.message.reply_text(text, reply_markup=keyboard())  # можно добавить reply_markup в каждую строку


def talk_to_me(bot, update):
    user_text = update.message.text
    # print(user_text)
    update.message.reply_text(user_text)


def get_contact(update):
    print(update.message.contact)
    update.message.reply_text('Спасибо!')


def get_location(update):
    print(update.message.location)
    update.message.reply_text('Спасибо!')


def main():
    """Run the bot."""
    global update_id
    # Telegram Bot Authorization Token
    # bot = telegram.Bot(TOKEN_FOR_BOT)

    # get the first pending update_id, this is so we can skip over it in case
    # we get an "Unauthorized" exception.
    # try:
    #    update_id = bot.get_updates()[0].update_id
    # except IndexError:
    #    update_id = None

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO,
                        filename='bot.log'
                        )
    updater = Updater(TOKEN_FOR_BOT)

    updater.bot._msg_queue = mq.MessageQueue()
    updater.bot._is_messages_queued_default = True

    dp = updater.dispatcher

    updater.job_queue.run_repeating(send_updates, interval=5)

    anketa = ConversationHandler(
        entry_points=[RegexHandler('^(Заполнить анкету)$', anketa_start, pass_user_data=True)],
        states={
            "name": [MessageHandler(Filters.text, anketa_get_name, pass_user_data=True)],
            "rating": [RegexHandler('^(1|2|3|4|5)$', anketa_rating, pass_user_data=True)],
            "comment": [MessageHandler(Filters.text, anketa_comment, pass_user_data=True),
                        CommandHandler('skip', anketa_skip_comment, pass_user_data=True)]
        },
        fallbacks=[MessageHandler(Filters.text | Filters.video | Filters.photo | Filters.document,
                                  dontknow, pass_user_data=True)]
    )
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("planet", planet, pass_args=True))
    dp.add_handler(CommandHandler("calc", calculator, pass_args=True))
    dp.add_handler(CommandHandler("wordcount", wordcount, pass_args=True))
    dp.add_handler(CommandHandler("next_full_moon", next_full_moon, pass_args=True))
    dp.add_handler(CommandHandler("cities", start_game, pass_args=True))
    dp.add_handler(CommandHandler("image", send_picture))
    # dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_handler(anketa)
    dp.add_handler(MessageHandler(Filters.photo, check_user_photo, pass_user_data=True))

    dp.add_handler(CallbackQueryHandler(inline_button_pressed))
    dp.add_handler(CommandHandler("subscribe", subscribe))
    dp.add_handler(CommandHandler("unsubscribe", unsubscribe))

    dp.add_handler(
        CommandHandler("alarm", set_alarm, pass_args=True, pass_job_queue=True)
    )

    dp.add_handler(MessageHandler(Filters.contact, get_contact, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.location, get_location, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me, pass_user_data=False))
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


# 49938425 - пример id, который меняется с каждой новой сессии (update_id)
# 144091076 - неизменный id (update.message.chat.id)


if __name__ == '__main__':
    main()
