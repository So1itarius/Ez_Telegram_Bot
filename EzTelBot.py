import logging
import telegram
from telegram.error import NetworkError, Unauthorized
from time import sleep

from answers import get_answer
from settings import token_for_bot

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
    text = 'Вызван /start'
    print(text)
    update.message.reply_text(text)


def echo(bot):
    """Echo the message the user sent."""
    global update_id
    # Request updates after the last update_id
    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1

        if update.message:  # your bot can receive updates without messages
            # Reply to the message
            if update.message.text == ("/start"):
                greet_user(update)
            if update.message.text.split()[0] == ("/planet"):
                update.message.reply_text(get_answer(update.message.text.split()[1]))
            else:
                update.message.reply_text(update.message.text)


if __name__ == '__main__':
    main()
