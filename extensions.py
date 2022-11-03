import requests
import json
from bs4 import BeautifulSoup
from config import keys, icons, HEADERS
from telebot import types


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
                rates.append(str(round(1 / v, 2)) + 'р.')
        text = f'<b>Вот курсы доступных валют (ЦБ) к рублю на {date}:</b>\n\n'
        for i, v in dict(zip(keys.keys(), rates)).items():
            text += f"<code>{i + ' ' * (15 - len(i))}</code>{v}\n"
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
            raise APIException('❗Количество параметров должно равняться 3❗')

        base, quote, amount = values
        base = base.lower()
        quote = quote.lower()

        if quote == base:
            raise APIException('❗Нельзя конвертировать одинаковые валюты❗')

        if quote not in keys or base not in keys:
            raise APIException(f'❗Не удалось обработать валюту❗')

        try:
            amount = float(amount)
        except ValueError:
            raise APIException('❗Не удалось обработать количество❗')

        base_ticker = keys[base]
        quote_ticker = keys[quote]

        result = f'{amount} {icons[base_ticker]} = ' \
                 f'{round((rates[quote_ticker] / rates[base_ticker]) * amount, 2)} ' \
                 f'{icons[quote_ticker]}'
        return result  # В выводе вместо вводимых пользователем названий валют я использовал соответствующие им unicode-символы чтобыизбежать путаницы с окончаниями

    @staticmethod
    def get_news():
        response = requests.get('https://1prime.ru/Forex/', HEADERS).text
        bs = BeautifulSoup(response, 'lxml')
        main = bs.find('div', class_='rubric-list__articles').find_all('article', class_='rubric-list__article')
        latestdate = main[0].find('time').get('datetime')[:10]
        latestnews = []
        for a in main:
            if a.find('time').get('datetime')[:10] == latestdate:
                latestnews.append(a)
        result = f'<b>Новости на {".".join(latestdate.split("-")[::-1])}:</b>\n\n'

        count = 0
        urls_list = []

        for i in latestnews:
            count += 1
            temp = i.find_all('a')[1]
            url = 'https://1prime.ru/' + temp.get('href')
            urls_list.append(url)
            title = temp.getText()
            result += f'{count})  {title}.\n'

        return result

    @staticmethod
    def get_news_text(number):
        response = requests.get('https://1prime.ru/Forex/', HEADERS).text
        bs = BeautifulSoup(response, 'lxml')
        main = bs.find('div', class_='rubric-list__articles').find_all('article', class_='rubric-list__article')
        latestdate = main[0].find('time').get('datetime')[:10]
        latestnews = []
        for a in main:
            if a.find('time').get('datetime')[:10] == latestdate:
                latestnews.append(a)

        urls_list = []

        for i in latestnews:
            url = 'https://1prime.ru/' + i.find_all('a')[1].get('href')
            urls_list.append(url)

        return f'Hello {urls_list[int(number) - 1]}'


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
    @staticmethod
    def get_news(bot, message):
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

        return bot.send_message(message.chat.id, result, parse_mode='HTML',
                                disable_web_page_preview=True, reply_markup=inline_markup)

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
        text += f'\n<a href="{call.data}">Источник</a>'
        return bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                     text=text, reply_markup=Kbds.get_back_btn(),
                                     disable_web_page_preview=True, parse_mode='HTML')

    @staticmethod
    def back(bot, call):  # очень топорная реализация кнопки "назад", но лучше я пока ничего не придумал(
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

        return bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                     text=result, parse_mode='HTML', disable_web_page_preview=True,
                                     reply_markup=inline_markup)
