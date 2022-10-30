import telebot
from config import BOT_TOKEN
from keyboard import markup
from extensions import Exchange, APIException


bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def welcome(message):
    wel = 'Для работы с ботом введите команду вида:\n<имя валюты> <в какую валюту перевести> <количество переводимой валюты>' \
          ' \nЧтобы узнать доступные валюты и их курсы к рублю нажмите кнопку' \
          ' "Курсы доступных валют" или введите /value'
    bot.reply_to(message, wel, reply_markup=markup)

@bot.message_handler(commands=['value'])
def val(message):
    bot.send_message(message.chat.id, Exchange.get_dayly_rates())

@bot.message_handler()
def handl(message):
    if message.text == '📈 Курсы доступных валют':
        bot.send_message(message.chat.id, Exchange.get_dayly_rates())
    else:
        try:
            bot.reply_to(message, Exchange.get_price(message.text))
        except APIException as e:
            bot.reply_to(message, f'Ошибка ввода!\n{e}')
        except Exception as e:
            bot.reply_to(message, f'Не удалось обработать команду\n{e}')


if __name__ == '__main__':
    bot.infinity_polling()