import telebot
import requests
from bs4 import BeautifulSoup
from auth_data import token


def get_data():  # Функция для парсинга страниц интернет-магазина
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    with open('AppleWatch.html', 'w', encoding='UTF-8') as file:  # Парсим страницу с часами
        r = requests.get(url='https://aj.ru/watch.html', headers=headers)
        file.write(r.text)
    with open('AJ.html', 'w', encoding='UTF-8') as file:  # Парсим страницу с остальной техникой
        r = requests.get(url='https://aj.ru/index.html', headers=headers)
        file.write(r.text)


def get_price(aj_type, name=''):  # Функция для получения стоимости техники
    # Часы. Для них на сайте отдельная страница
    if aj_type == 'Apple Watch':
        with open('AppleWatch.html', encoding='UTF-8') as file:
            src = file.read()
        soup = BeautifulSoup(src, 'lxml')
        watch_names_list = [i.text for i in soup.find_all('h1')]  # Список названий всех часов и акксессуаров
        if len(name) > 0:
            temp = soup.find_all('li', class_=f'{name}')
            watch_dict = {}
            for line in temp:
                temp = line.find('div', class_='price-block').text.strip()
                watch_dict.setdefault(line.find('h2').text, temp)
            return watch_dict
        return watch_names_list

    else:
        with open('AJ.html', encoding='UTF-8') as file:
            src = file.read()
        soup = BeautifulSoup(src, 'lxml')

    # Айфоны
    if aj_type == 'iPhone':
        temp = soup.find_all('h2')
        phone_names_list = [i.text for i in temp if 'iPhone' in i.text]  # Список названий всех айфонов
        if len(name) > 0:
            temp = soup.find_all('li', id=f'{name.lower().replace(" ", "_") + "_"}')
            phone_list = []
            for line in temp:
                phone_list = [i.text for i in line.find_all('ul')]
            return phone_list
        return phone_names_list

    # Наушники
    if aj_type == 'AirPods':
        temp = soup.find_all('h2')
        airpods_names_list = [i.text for i in temp if 'AirPods' in i.text]  # Список названий всех наушников
        if len(name) > 0:
            if name == 'AirPods (окрашенные)':
                name = name.replace(' (окрашенные)', '-paint')
            temp = soup.find_all('li', id=f'{name.lower().replace(" ", "_") + "_"}')
            airpods_list = []
            for line in temp:
                airpods_list = [i.text for i in line.find_all('ul')]
            return airpods_list
        return airpods_names_list

    # Геометки
    if aj_type == 'AirTag':
        airtag_list = []
        for line in soup.find_all('li', id='airtag'):
            airtag_list = [i.text for i in line.find_all('ul')]
        return airtag_list

    # Планшеты
    if aj_type == 'iPad':
        temp = soup.find_all('h2')
        ipad_names_list = [i.text for i in temp if 'iPad' in i.text]  # Список названий всех планшетов
        if len(name) > 0:
            name = name.replace('iPad Pro', 'ipadpro').replace('iPad Air ', 'ipad_air_') + '_'
            name = name.lower().replace('"', '').replace(' ', '-').replace(',9', '')
            temp = soup.find_all('li', id=f"{name}")
            ipad_list = []
            for line in temp:
                ipad_list = [i.text for i in line.find_all('ul')]
            return ipad_list
        return ipad_names_list


def telegram_bot(token):  # Бот
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=['start'])  # Кнопки списка техники
    def start_message(message):
        get_data()
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
        bot.reply_markup = None

    @bot.message_handler(content_types=['text'])  # Кнопки выбора модели
    def send_text(message):
        if message.text == 'iPhone':
            markup = telebot.types.InlineKeyboardMarkup()
            for i in get_price(message.text):
                markup.add(telebot.types.InlineKeyboardButton(i, callback_data=i))
            bot.send_message(message.chat.id, 'Какой iPhone интересуют?', reply_markup=markup)
        elif message.text == 'AirPods':
            markup = telebot.types.InlineKeyboardMarkup()
            for i in get_price(message.text):
                markup.add(telebot.types.InlineKeyboardButton(i, callback_data=i))
            bot.send_message(message.chat.id, 'Какие AirPods интересуют?', reply_markup=markup)
        elif message.text == 'AirTag':
            for i in get_price(message.text, message.text):
                bot.send_message(message.chat.id, f'{i}')
        elif message.text == 'Apple Watch':
            markup = telebot.types.InlineKeyboardMarkup()
            for i in get_price(message.text):
                markup.add(telebot.types.InlineKeyboardButton(i, callback_data=i))
            bot.send_message(message.chat.id, 'Какой серии часы интересуют?', reply_markup=markup)
        elif message.text == 'iPad':
            markup = telebot.types.InlineKeyboardMarkup()
            for i in get_price(message.text):
                markup.add(telebot.types.InlineKeyboardButton(i, callback_data=i))
            bot.send_message(message.chat.id, 'Какой iPad интересуют?', reply_markup=markup)
        elif message.text == 'Macbook':
            bot.send_message(message.chat.id, 'Функционал недоступен')

    @bot.callback_query_handler(func=lambda call: True)  # Обработка данных с кнопки для получения стоимости модели
    def callback(call):
        try:
            if call.data in get_price('Apple Watch'):  # Получаем стоимость часов
                d = {'Apple Watch Series 8': 'for-watch-8',
                     'Apple Watch Series SE 2022': 'for-watch-SE-2022',
                     'Apple Watch Series 8 Stainless Steel': 'for-watch-8',
                     'Apple Watch Ultra': 'for-watch-ultra',
                     'Apple Watch Series 7': 'for-watch-7',
                     'Apple Watch Series SE': 'for-watch-SE',
                     'Apple Watch Nike': 'for-watch-nikeplus',
                     'Ремешки': 'for-bands',
                     'Аксессуары': 'for-accessories'}
                for i in get_price(aj_type='Apple Watch', name=d[call.data]).items():
                    bot.send_message(call.message.chat.id, f'{i[0]} {i[1]}')
                bot.send_message(call.message.chat.id, 'Чтобы узнать стоимость другой продукции, нажми /start')
            if call.data in get_price('iPhone'):  # Получаем стоимость айфона
                for i in get_price(aj_type='iPhone', name=call.data):
                    bot.send_message(call.message.chat.id, f'{i}')
                bot.send_message(call.message.chat.id, 'Чтобы узнать стоимость другой продукции, нажми /start')
            if call.data in get_price('AirPods'):  # Получаем стоимость наушников
                for i in get_price(aj_type='AirPods', name=call.data):
                    bot.send_message(call.message.chat.id, f'{i}')
                bot.send_message(call.message.chat.id, 'Чтобы узнать стоимость другой продукции, нажми /start')
            for i in get_price(aj_type='iPad', name=call.data):  # Получаем стоимость планшета
                bot.send_message(call.message.chat.id, f'{i}')
                bot.send_message(call.message.chat.id, 'Чтобы узнать стоимость другой продукции, нажми /start')
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=call.data, reply_markup=None)
        except Exception as ex:
            print(ex)
            bot.send_message(call.message.chat.id, 'Что-то не так')
            return

    bot.polling()


def main():
    telegram_bot(token)


if __name__ == '__main__':
    main()
