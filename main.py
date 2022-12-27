import telebot
import traceback

from telebot import types
from extensions import APIException, Convertor
from config import TOKEN, tickers

bot = telebot.TeleBot(TOKEN)
conv = Convertor()


if __name__ == '__main__':

    def conv_keyboard(base=None):
        conv_markup = telebot.types.InlineKeyboardMarkup()
        conv_buttons = []
        for t in tickers.keys():
            if t != base:
                button = types.InlineKeyboardButton(t, callback_data=t)
                conv_buttons.append(button)
        conv_markup.add(*conv_buttons)
        return conv_markup

    @bot.message_handler(commands=['start', 'help'])
    def start_message(m):
        conv.base = ''
        conv.quote = ''
        help_markup = telebot.types.InlineKeyboardMarkup()
        help_markup.add(types.InlineKeyboardButton('Список валют', callback_data='values'))
        text = 'Привет! Я могу посчитать стоимость одной валюты в другой. \
 Чтобы увидеть перечень доступных валют, нажми кнопку ниже ↓'
        bot.send_message(m.chat.id, text, reply_markup=help_markup)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_button(call):
        c_id = call.message.chat.id
        m_id = call.message.message_id
        try:
            if call.data == 'values':
                text = 'Первой выберите конвертируемую валюту:'
                base_markup = conv_keyboard()
                bot.send_message(c_id, text, reply_markup=base_markup)
                bot.edit_message_reply_markup(c_id, m_id)

            if (call.data in tickers.keys()) and not conv.base:
                conv.base = call.data
                call.data = None
                conv.isRunning = True
                text = f'Первой валютой выбрано: {conv.base}.\nВторой выберите валюту, в которую нужно конвертировать:'
                receive_markup = conv_keyboard(conv.base)
                bot.send_message(c_id, text, reply_markup=receive_markup)
                bot.edit_message_reply_markup(c_id, m_id)

            if (call.data in tickers.keys()) and not conv.quote and conv.isRunning:
                conv.quote = call.data
                text = f'Второй валютой выбрано: {conv.quote}.\nТеперь введите количество первой валюты:'
                bot.send_message(c_id, text)
                bot.edit_message_reply_markup(c_id, m_id)

        except Exception as err:
            traceback.print_tb(err.__traceback__)
            bot.send_message(c_id,  f'Неизвестная ошибка:\n{err}\nНачните сначала: /start')


    @bot.message_handler(content_types=['text'])
    def converter(m):
        if conv.base and conv.quote:
            ask = m.text.split(' ')

            try:
                if len(ask) != 1:
                    raise APIException('Неверное количество значений!\n Введите одно число!')
                ask.insert(0, conv.quote)
                ask.insert(0, conv.base)
                answer = Convertor.get_price(*ask)
            except APIException as err:
                bot.reply_to(m, f'Ошибка в команде:\n{err}')
            except Exception as err:
                bot.reply_to(m, f'Неизвестная ошибка:\n{err}\nНачните сначала: /start')
            else:
                text = f'\nДля возврата в начало введите /start'
                bot.send_message(m.chat.id, answer + text)
        else:
            text = f'Я не понимаю о чём вы ☺\n   введите /help'
            bot.send_message(m.chat.id, text)


    bot.polling(none_stop=True)
