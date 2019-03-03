import logging
import telegram
from telegram.error import NetworkError, Unauthorized
from time import sleep

from answers import get_answer, next_full_moon, calc, wordcount
from settings import token_for_bot
from translator import translator

update_id = None


def main():
    """Run the bot."""
    global update_id
    # Telegram Bot Authorization Token
    bot = telegram.Bot(token_for_bot)

    # get the first pending update_id, this is so we can skip over it in case
    # we get an "Unauthorized" exception.
    try:
        update_id = bot.get_updates()[0].update_id
    except IndexError:
        update_id = None

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO,
                        filename='bot.log'
                        )

    while True:
        try:
            echo(bot)
        except NetworkError:
            sleep(1)
        except Unauthorized:
            # The user has removed or blocked the bot.
            update_id += 1


def greet_user(update):
    text = 'Вызван /start, ВНИМАНИЕ БОТ НЕ ЗАСТРАХОВА ОТ ВВОДА ВСЯКОЙ ХУЙНИ!'
    print(text)
    update.message.reply_text(text)


def echo(bot):
    """Echo the message the user sent."""
    global update_id, update
    # Request updates after the last update_id
    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1
    try:
        if update.message:  # your bot can receive updates without messages
            # Reply to the message
            if update.message.text == ("/start"):
                greet_user(update)
            elif update.message.text.split()[0] == ("/planet"):
                update.message.reply_text(get_answer(translator(update.message.text.split()[1].capitalize())))
            elif update.message.text.split()[0] == ("/next_full_moon"):
                update.message.reply_text(next_full_moon(update.message.text.split()[1]))
            elif update.message.text.split(' ', maxsplit=1)[0] == ("/calc"):
                update.message.reply_text(calc(update.message.text.split(' ', maxsplit=1)[1]))
            elif update.message.text.split(' ', maxsplit=1)[0] == ("/wordcount"):
                update.message.reply_text(wordcount(update.message.text.split(' ', maxsplit=1)[1]))

            else:
                update.message.reply_text(update.message.text,)

    except IndexError:
        update.message.reply_text("У этой команды должен быть 1 аргумент")


if __name__ == '__main__':
    main()
