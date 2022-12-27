import requests
import json
from config import tickers, source

class APIException(Exception):
    pass

class Convertor:
    isRunning = False
    base = ''
    quote = ''
    
    @staticmethod
    def get_price(base, quote, amount):
        try:
            base_key = tickers[base]
        except KeyError:
            raise APIException(f'Валюта "{base}" не найдена!\nНачните сначала: /start')

        try:
            receive_key = tickers[quote.lower()]
        except KeyError:
            raise APIException(f'Валюта "{quote}" не найдена!\nНачните сначала: /start')

        if base_key == receive_key:
            raise APIException(f'Конвертация невозможна: обе валюты "{base}"!\nНачните сначала: /start')

        try:
            amount = float(amount)
        except ValueError:
            raise APIException(f'Не удалось обработать количество "{amount}"!\n Введите число!')

        r = requests.get(f'{source}{base_key}/{receive_key}')
        rates = json.loads(r.content)
        cost = round((rates * amount), 2)
        message = f'"{base}" в количестве:  {amount}\n   равно\n"{quote}" в количестве:  {cost} '
        return message
