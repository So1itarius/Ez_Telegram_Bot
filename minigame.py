import random
import requests
from parsel import Selector

game_dict = {}


# Парсим сайт с городами, создавая список. Присваиваем список пользователю
def new_cities_list():
    game_page = requests.get("http://xn----7sbiew6aadnema7p.xn--p1ai/alphabet.php")
    sel = Selector(game_page.text)

    cities = sel.css('.common-text ul a::text').extract()
    return cities


def game_move(update, city):
    chat_id = update.message.chat.id
    cities_list = game_dict.get(chat_id)
    last_letter = cities_list.pop(cities_list.index(city))[-1].upper()  # Выделяем последнюю букву
    a = [i for i in cities_list if i.startswith(last_letter)]  # Список городов, начинающихся на нужную букву
    if len(a) == 0:
        return f"Города на {last_letter} нет, вы победили!"
    random_from_a = random.choice(a)  # Рандомно выбираем город на нужную букву
    cities_list.remove(random_from_a)
    game_dict[chat_id] = cities_list
    return f"{random_from_a}, ваш ход"


def start_game(bot, update, args):
    try:
        city = args[0]
        update.message.reply_text(game_move(update, city))
    except (IndexError, ValueError):
        update.message.reply_text("Введите город как первый ход, после /cities")
