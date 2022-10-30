import requests
import json
from config import keys


class APIException(Exception):
    pass


class Exchange:
    @staticmethod
    def get_dayly_rates():
        response = requests.get('https://www.cbr-xml-daily.ru/latest.js').text
        js = (json.loads(response))
        date = '.'.join(js['date'].split('-')[::-1])
        r = js['rates']
        rates = []
        for i, v in r.items():
            if i in keys.values():
                rates.append(str(round(1/v, 2)) + 'р.')
        text = f'Вот курсы доступных валют в рублях на {date}:\n\n'
        for i, v in dict(zip(keys.keys(), rates)).items():
            text += f'{i} {v}\n'

        return text.strip('\n')

    @staticmethod
    def get_price(message):
        response = requests.get('https://www.cbr-xml-daily.ru/latest.js').text
        js = (json.loads(response))['rates']
        values = message.split(' ')
        rates = {'RUB': 1}
        for i, v in js.items():
            if i in keys.values():
                rates.update({i: v})

        if len(values) != 3:
            raise APIException('Количество параметров должно равняться 3')

        base, quote, amount = values

        if quote == base:
            raise APIException('Нельзя конвертировать одинаковые валюты')

        if quote not in keys or base not in keys:
            raise APIException(f'Не удалось обработать валюту.')

        try:
            amount = float(amount)
        except ValueError:
            raise APIException('Не удалось обработать количество')

        base_ticker = keys[base]
        quote_ticker = keys[quote]

        result = f'{amount} {base_ticker} сейчас стоит ' \
                 f'{round((rates[quote_ticker]/rates[base_ticker])*amount, 2)} ' \
                 f'{quote_ticker}'
        return result  #В выводе вместо вводимых пользователем названий валют я использовал тикеры чтобы не было путаницы с окончаниями.









