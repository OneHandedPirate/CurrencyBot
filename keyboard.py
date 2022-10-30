from telebot import types


markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
ratesBtn = types.KeyboardButton('📈 Курсы доступных валют')
markup.add(ratesBtn)