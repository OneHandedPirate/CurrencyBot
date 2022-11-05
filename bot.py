import asyncio
import logging
import telebot
from config import keys, WELCOME
from extensions import Exchange, Kbds, News, APIException
from botToken import BOT_TOKEN
from telebot.async_telebot import AsyncTeleBot

bot = AsyncTeleBot(BOT_TOKEN, disable_web_page_preview=True, parse_mode='HTML')
logger = telebot.logger.setLevel(logging.DEBUG)

@bot.message_handler(commands=['start', 'help'])
async def welcome(message):
    await bot.reply_to(message, WELCOME, reply_markup=Kbds.get_replykbd(), parse_mode=None)

@bot.message_handler(commands=['value'])
async def value(message):
    val = '🔄 Валюты, доступные для конвертации и их ключи:\n'
    for key, lst in keys.items():
        val += f'\n{lst[2]}   ➡   {key}'
    await bot.send_message(message.chat.id, val)

@bot.message_handler(content_types=['text'])
async def handl(message):
    if message.text == '📈 Курсы доступных валют':
        await bot.send_message(message.chat.id, Exchange.get_dayly_rates())
    elif message.text == '📰 Новости валютных рынков':
        await News.get_news(bot, message=message)
    else:
        try:
            await bot.reply_to(message, Exchange.get_price(message.text))
        except APIException as e:
            await bot.reply_to(message, f'⛔ Ошибка ввода!\n\n{e}')
        except Exception as e:
            await bot.reply_to(message, f'⛔ Не удалось обработать команду\n{e}')

@bot.callback_query_handler(func=lambda call: True)
async def callback(call):
    if call.data == 'back':
        await News.get_news(bot, call=call)
    else:
        await News.get_text(bot, call)


if __name__ == '__main__':
    asyncio.run(bot.infinity_polling())