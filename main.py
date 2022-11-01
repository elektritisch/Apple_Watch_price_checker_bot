import telebot
import requests
from bs4 import BeautifulSoup
from auth_data import token


def get_data(url, type):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
    }

    r = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    watch_name = soup.find_all('li', class_=f'for-watch-{type}')
    watch_dict = {}
    for line in watch_name:
        temp = line.find('div', class_='price-block').text.strip()
        watch_dict.setdefault(line.find('h2').text, (temp))
    return watch_dict


def telegram_bot(token):
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=['start'])
    def start_message(message):
        bot.send_message(message.chat.id, f'Привет, {message.chat.first_name}! Я могу показать цены на технику Apple')
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        btn_iphone = telebot.types.KeyboardButton('iPhone')
        btn_airpods = telebot.types.KeyboardButton('AirPods')
        btn_airtag = telebot.types.KeyboardButton('AirTag')
        btn_watch = telebot.types.KeyboardButton('Apple Watch')
        btn_ipad = telebot.types.KeyboardButton('iPad')
        btn_macbook = telebot.types.KeyboardButton('Macbook')
        markup.add(btn_iphone, btn_airpods, btn_airtag, btn_watch, btn_ipad, btn_macbook)
        bot.send_message(message.chat.id, 'Какая продукция Apple интересует?', reply_markup=markup)

    @bot.message_handler(content_types=['text'])
    def send_text(message):
        if message.text == 'iPhone':
            bot.send_message(message.chat.id, 'Функционал недоступен')
        elif message.text == 'AirPods':
            bot.send_message(message.chat.id, 'Функционал недоступен')
        elif message.text == 'AirTag':
            bot.send_message(message.chat.id, 'Функционал недоступен')
        elif message.text == 'Apple Watch':
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            btn7 = telebot.types.KeyboardButton('7')
            btn8 = telebot.types.KeyboardButton('8')
            markup.add(btn7, btn8)
            bot.send_message(message.chat.id, 'Какой серии часы интересуют?', reply_markup=markup)
        elif message.text == 'iPad':
            bot.send_message(message.chat.id, 'Функционал недоступен')
        elif message.text == 'Macbook':
            bot.send_message(message.chat.id, 'Функционал недоступен')

        elif message.text in '78':
            try:
                for i in get_data('https://aj.ru/watch.html', type=message.text).items():
                    bot.send_message(message.chat.id, f'{i[0]} {i[1]}')
                bot.send_message(message.chat.id, 'Чтобы узнать стоимость другой продукции, нажми /start')
            except Exception as ex:
                print(ex)
                bot.send_message(message.chat.id, 'Что-то не так')
        else:
            bot.send_message(message.chat.id, 'Чтобы запустить меня заново, нажми /start')

    bot.polling()


def main():
    telegram_bot(token)


if __name__ == '__main__':
    main()
