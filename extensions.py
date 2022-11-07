import json
import requests
from bs4 import BeautifulSoup
from config import keys, HEADERS
from telebot import types


class APIException(Exception):
    pass


class Exchange:
    # Получаем актуальные курсы валют, указанных в keys.
    @staticmethod
    def get_dayly_rates():
        response = requests.get('https://www.cbr-xml-daily.ru/latest.js').text
        js = (json.loads(response))
        date = '.'.join(js['date'].split('-')[::-1])
        r = js['rates']
        rates = []
        for i, v in r.items():
            for cur in keys.values():
                if i in cur[0]:
                    rates.append(str(round(1 / v, 2)) + 'р.')
        text = f'<b>Вот курсы доступных валют (ЦБ) к рублю на {date}:</b>\n\n'
        for v, i in dict(zip(rates, keys.values())).items():
            #форматирование в виде применяется только для того, чтобы выровнять колонку с ценами валют.
            text += f"<code>{i[2] + ' ' * (22 - len(i[2]))}</code>{v}\n"
        return text.strip('\n')

    #Конвертор валют
    @staticmethod
    def get_price(message):
        response = requests.get('https://www.cbr-xml-daily.ru/latest.js').text
        js = (json.loads(response))['rates']
        values = message.split(' ')
        rates = {'RUB': 1}
        for i, v in js.items():
            for cur in keys.values():
                if i == cur[0]:
                    rates.update({i: v})

        if len(values) != 3:
            raise APIException('❗Количество параметров должно равняться 3❗')

        base, quote, amount = values
        base = base.lower()
        quote = quote.lower()

        if quote == base:
            raise APIException('❗Нельзя конвертировать одинаковые валюты❗')

        if quote not in keys or base not in keys:
            raise APIException(f'❗Не удалось обработать ключ '
                               f'валюты {"№1" if base not in keys else "№2"}❗')
        try:
            amount = float(amount)
        except ValueError:
            raise APIException('❗Не удалось обработать количество❗')

        base_ticker = keys[base][0]
        quote_ticker = keys[quote][0]

        result = f'{amount} {keys[base][1]} = ' \
                 f'{round(rates[quote_ticker] / rates[base_ticker] * amount, 2)} ' \
                 f'{keys[quote][1]}'
        return result  # В выводе вместо вводимых пользователем ключей валют я использовал соответствующие им unicode-символы чтобы избежать путаницы с окончаниями


#Класс кнопок
class Kbds:
    @staticmethod
    def get_back_btn():
        back = types.InlineKeyboardMarkup()
        return back.add(types.InlineKeyboardButton('Назад', callback_data='back'))

    @staticmethod
    def get_replykbd():
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        ratesbtn = types.KeyboardButton('📈 Курсы доступных валют')
        newsbtn = types.KeyboardButton('📰 Новости валютных рынков')
        return markup.add(ratesbtn, newsbtn)


class News:
    # Получаем список новостей, ссылок на их тексты и кнопки и ограничиваем его последней датой.
    # Можно было бы ограничить список определенным количеством (10-15,например),
    # чтобы избежать ситуации когда обновляется дата и показывается только одна новость, но я решил оставить так.
    @staticmethod
    def get_news(bot, message=None, call=None):
        response = requests.get('https://1prime.ru/Forex/', HEADERS).text
        bs = BeautifulSoup(response, 'lxml')
        main = bs.find('div', class_='rubric-list__articles').find_all('article', class_='rubric-list__article')
        latestdate = main[0].find('time').get('datetime')[:10]
        latestnews = []
        for a in main:
            if a.find('time').get('datetime')[:10] == latestdate:
                latestnews.append(a)
        result = f'⚡ <b>Новости на {".".join(latestdate.split("-")[::-1])}:</b> ⚡\n\n'

        count = 0
        urls_list = []

        for i in latestnews:
            count += 1
            temp = i.find_all('a')[1]
            url = 'https://1prime.ru/' + temp.get('href')
            urls_list.append(url)
            title = temp.getText()
            result += f'{count})  {title}.\n'

        inline_markup = types.InlineKeyboardMarkup(row_width=5)
        num = 0
        btns = []
        for url in urls_list:
            num += 1
            btns.append(types.InlineKeyboardButton(f'{num}', callback_data=f'{url}'))
        inline_markup.add(*btns)

        if message:
            return bot.send_message(message.chat.id, result, reply_markup=inline_markup)
        elif call:
            return bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                         text=result, reply_markup=inline_markup)

    # Получаем текст новости, распарсив страницу которая передается в callback_data.
    @staticmethod
    def get_text(bot, call):
        response = requests.get(call.data, HEADERS).text
        bs = BeautifulSoup(response, 'lxml')
        text = ''
        title = bs.find(class_='article-header__title').get_text()
        text += f"⚡ <b>{title}</b>\n\n"
        article_lst = bs.find('div', class_='article-body__content').find_all('p')
        for p in article_lst:
            if p.get_text().isupper():
                text += f'\n      {p.get_text()}\n\n'
            else:
                text += f'      {p.get_text()}\n'
        text += f'\n👉  <a href="{call.data}">Источник</a>'
        # Если текст слишком длинный для 1 сообщения - обрезаем его и отправляем
        # пользователя читать источник. Это бывает крайне редко.
        if len(text) > 4000:
            text = text[:4000]
            text += f'...  \n\n👉  <a href="{call.data}"> Продолжение в источнике</a>'

        return bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                     text=text, reply_markup=Kbds.get_back_btn(),
                                     disable_web_page_preview=True)