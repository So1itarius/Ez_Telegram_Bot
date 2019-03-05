import re
from datetime import datetime

import ephem





def get_answer(st):
    try:
        today = datetime.now(tz=None).strftime('%Y/%m/%d')
        print("Сегодня", today)

        # planet = eval("ephem." + st)(today)
        planet = getattr(ephem, st)(today)
        return ephem.constellation(planet)

    except AttributeError:
        return "Нет такой планеты"


def next_full_moon(day):

    return ephem.next_full_moon(day)


def calc(st):
    try:
        match = re.fullmatch('[-+]?\d([-+/*]?\d)+', st)
        a = st if match else "'Неверный ввод'"
        return eval(a)

    except ZeroDivisionError:
        return "Деление на ноль"


def wordcount(st):
    a = len(re.findall(r'\w+', st))
    return f"Количество слов: {a}"
