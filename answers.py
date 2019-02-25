from datetime import datetime

import ephem

def get_answer(st):
    #import ephem
    try:
        today = datetime.now(tz=None).strftime('%Y/%m/%d')
        print("Сегодня", today)
        planet = eval("ephem." + st)(today)
        return ephem.constellation(planet)

    except AttributeError:
        return "Нет такой планеты"

