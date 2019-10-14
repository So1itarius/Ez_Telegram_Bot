from clarifai.rest.client import ClarifaiApp
from telegram import KeyboardButton, ReplyKeyboardMarkup

import settings


def keyboard():
    contact_button = KeyboardButton('Контактные данные', request_contact=True)
    location_button = KeyboardButton('Геолокация', request_location=True)
    my_keyboard = ReplyKeyboardMarkup([['/image'],
                                       [contact_button, location_button],
                                       ["Заполнить анкету"]
                                       ],
                                      resize_keyboard=True)
    return my_keyboard


def is_cat(file_name):
    image_has_cat = False
    app = ClarifaiApp(api_key=settings.CLARIFAI_API_KEY)
    model = app.public_models.general_model
    response = model.predict_by_filename(file_name, max_concepts=5)
    # import pprint
    # pp = pprint.PrettyPrinter(indent=2)
    # pp.pprint(response)
    if response["status"]["code"] == 10000:
        for concept in response['outputs'][0]['data']['concepts']:
            if concept['name'] == 'man':
                image_has_cat = True
    return image_has_cat


