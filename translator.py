import requests

from settings import TOKEN_FOR_YANDEX_TRANSLATOR


def translator(text):
    url = 'https://translate.yandex.net/api/v1.5/tr.json/translate?'
    return requests.post(url, data={'key': TOKEN_FOR_YANDEX_TRANSLATOR, 'text': text, 'lang': 'ru-en'}).json()['text'][0]
