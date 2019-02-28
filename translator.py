import requests

from settings import token_for_yandex_translator


def translator(text):
    url = 'https://translate.yandex.net/api/v1.5/tr.json/translate?'
    return requests.post(url, data={'key': token_for_yandex_translator, 'text': text, 'lang': 'ru-en'}).json()['text'][0]
