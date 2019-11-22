
import telebot
from telebot import types
import sqlite3
from sqlite3 import Error
import telegram
import qrcode
from io import BytesIO
from datetime import date



TOKEN = '698801737:AAE4bn6E1aO1FfSsWoUbBG67-HUr6JPnO8s'
bot = telebot.TeleBot(TOKEN)

""""today = date.today()
x = str(today).split("-")
cur_month = x[1]
cur_day = x[2]
serial_num = '1'+cur_day+cur_month+'9'
"""


import os
from flask import Flask

app = Flask(__name__)

'''print(serial_num)
'''
"""--------------/START------------"""



def create_connection(db_file):
	conn = None
	try:
		conn = sqlite3.connect(db_file)
		return conn
	except Error as e:
		print(e)
 
	return conn



def do_query(db,sql_query):
	try:
		conn = create_connection(db)
		c = conn.cursor()
		c.execute(sql_query)
		conn.commit()
		c.close()
		conn.close()
	except Error as e:
		print(e)


def select_from(db, sql_query):
	try:
		conn = create_connection(db)
		cur = conn.cursor()
		cur.execute(sql_query)
		rows = cur.fetchall()
		conn.commit()
		cur.close()
		conn.close()
		return rows
	except Error as e:
		print(e)


#VARIABLES
db = r"Botdb.db"
table_create = """ CREATE TABLE IF NOT EXISTS clients (
			chat_id VARCHAR(255) UNIQUE NOT NULL,
			name VARCHAR(255) NULL,
			surname VARCHAR(255) NULL,
			sex VARCHAR(255) NULL,
			birth_date VARCHAR(255) NULL
		); """
check_tables = " SELECT * FROM clients;"


do_query(db,table_create)
'''print(select_from(db,check_tables))
'''

@bot.message_handler(commands=['start'])
def send_welcome(message):
	query = "SELECT * FROM clients  WHERE chat_id = " + str(message.from_user.id) + ";"
	rows = select_from(db,query)
	if rows != None and len(rows)>0:
		for i in rows:
			if i[1] == '':
				bot.send_message(message.from_user.id, "В прошлый раз вы не указали свое имя. Укажите ваше имя.");
				bot.register_next_step_handler(message, get_name);
			elif i[2] == '':
				bot.send_message(message.from_user.id, "В прошлый раз вы не указали свое фамилию. Укажите вашу фамилию.");
				bot.register_next_step_handler(message, get_surname);
			elif i[3] == '':
				bot.send_message(message.from_user.id, "В прошлый раз вы не указали свой пол. Укажите ваш пол буквой М или Ж.");
				bot.register_next_step_handler(message, get_sex);
			elif i[4] == '':
				bot.send_message(message.from_user.id, "В прошлый раз вы не указали свою дату рождения. Укажите вашу дату в формате ДД.ММ.ГГГГ.");
				bot.register_next_step_handler(message, start_handler);
			else:
				open_menu(message);
				

			if len(rows) > 1:
				break
		
	else:
		bot.reply_to(
			message,
			'Привет!\nЯ Бот SUN TEA! Вы впервые у нас, пожалуйста пройдите регистрацию');
		query = "INSERT INTO clients(chat_id,name,surname,sex,birth_date) VALUES (" + str(message.from_user.id) + ",'','','','')"
		do_query(db,query)
		bot.send_message(message.from_user.id, "Как вас зовут?");
		bot.register_next_step_handler(message, get_name);


"""--------------/REGISTRATION------------"""


def get_name(message):  # получаем фамилию
	name = message.text;
	query = " UPDATE clients SET name = '" + str(name) + "' WHERE chat_id = " + str(message.from_user.id) + " ;"
	do_query(db,query)
	bot.send_message(message.from_user.id, 'Какая у вас фамилия?');
	bot.register_next_step_handler(message, get_surname);


def get_surname(message):
	surname = message.text;
	query = " UPDATE clients SET surname = '" + str(surname) + "' WHERE chat_id = " + str(message.from_user.id) + " ;"
	do_query(db,query)
	bot.send_message(message.from_user.id, 'Укажите ваш пол буквой M или Ж');
	bot.register_next_step_handler(message, get_sex);


def get_sex(message):
	sex= message.text;
	query = " UPDATE clients SET sex = '" + str(sex) + "' WHERE chat_id = " + str(message.from_user.id) + " ;"
	do_query(db,query)
	bot.send_message(
	message.from_user.id,
	 'Укажите ваш день рождения.\nВведите в формате ДД.ММ.ГГГГ\nНапример: 12.10.1999');
	bot.register_next_step_handler(message, start_handler);



def start_handler(message):
	try:
		age = message.text;
		agesplit=age.split(".")
		print(agesplit)
		user_day = agesplit[0]
		user_month = agesplit[1]
		user_year = agesplit [2]

		if user_day.isdigit() == True and user_month.isdigit() == True and user_year.isdigit() == True:
			query = " UPDATE clients SET birth_date = '" + str(age) + "' WHERE chat_id = " + str(message.from_user.id) + " ;"
			do_query(db,query)
			bot.send_message(message.from_user.id, f'Спасибо, данные сохранены. Нажмите /start')

		else:
			bot.send_message(message.from_user.id, f'Вы не верно ввели дату рождения, пожалуйста укажите его в формате ДД.ММ.ГГГГ.\nНапример: 12.10.1999 ')
			bot.register_next_step_handler(message, start_handler);

	except:
		print("An exception occurred")
		bot.send_message(message.from_user.id, f'Вы не верно ввели дату рождения, пожалуйста укажите его в формате ДД.ММ.ГГГГ.\nНапример: 12.10.1999 ')
		bot.register_next_step_handler(message, start_handler);



"""--------------/REGISTRATION------------"""


def qrgenerate(user_id):
	global qr
	qr = qrcode.QRCode(
		version=1,
		box_size=15,
		border=5
	)
	qr_query="SELECT name,surname from clients WHERE chat_id = " + str(user_id) +';'
	rows = select_from(db,qr_query)
	for values in rows:
		for i in values:
			name = values[0]
			surname = values[1]

	data ="SUNTEAQR"+serial_num + surname + ' ' + name
	qr.add_data(data)
	qr.make(fit=True)
	img = qr.make_image(fill='black', back_color='white')

	bio = BytesIO()
	bio.name = 'qr.jpeg'
	img.save(bio, 'JPEG')
	bio.seek(0)
	return bio




@bot.message_handler(content_types=['text'])
def get_text_menu(message):
	if message.text == "📲 Получить скидку":
		try:
			bot.send_photo(message.from_user.id, 'https://ibb.co/wshz8hb')
			bot.send_message(message.from_user.id,"Предьявите qr-код кассиру и получите скидку 7%.")
		except Error as e:
			print(e)
		"""bot.send_photo(message.from_user.id, photo=qrgenerate(message.from_user.id))"""
		
	elif message.text == "📑 Меню SunTea":
		try:
			bot.send_photo(message.from_user.id, 'https://ibb.co/ydCZJpT')
		except Error as e:
			print(e)
	elif message.text == "📞Контакты SunTea":
		bot.send_message(message.from_user.id, """https://suntea.kz\n\ninstagram.com/sunteakz\n\ninfo@suntea.kz\n\n8 (727)317-07-44\n\n2й этаж, ТРЦ Спутник, Алматы, Казахстан""" );
	elif message.text == "🍹Акции SunTea":
		try:
			bot.send_photo(message.from_user.id, 'https://ibb.co/RTQGxsm')
			bot.send_message(message.from_user.id,"500 KZT.")
			bot.send_photo(message.from_user.id, 'https://ibb.co/DrvWBpg')
			bot.send_message(message.from_user.id,"1100 KZT.")
			bot.send_photo(message.from_user.id, 'https://ibb.co/BLM51D6')
			bot.send_message(message.from_user.id,"500 KZT.")
		except Error as e:
			print(e)
		
	elif message.text == "📋Условия программы лояльности":
		bot.send_message(message.from_user.id, """Вы можете получить скидку в размере 7% на каждую покупку.\nУсловия нашей программы лояльности, пройди один раз регистрацию в чат-боте Telegram, получай скидку 7% при каждой оплате.\n
Первым узнавай об акциях и скидках🔥 Воспользоваться скидкой могут только  зарегистрированные покупатели в нашем чат боте""" );
	elif message.text == "/help":
		bot.send_message(message.from_user.id, "Для более удобного пользования нашим ботом, мы предлагаем вам использовать кнопки" );
	else:
		bot.send_message(message.from_user.id, "Я вас не понимаю. Напишите /start или /help")



def open_menu(message):
	bot.send_message(message.from_user.id, "Привет! Я бот SUN TEA")
	markup = types.ReplyKeyboardMarkup(row_width=1)
	itembtn1 = types.KeyboardButton('📲 Получить скидку')
	itembtn2 = types.KeyboardButton('📑 Меню SunTea')
	itembtn3 = types.KeyboardButton('📞Контакты SunTea')
	itembtn4 = types.KeyboardButton('🍹Акции SunTea')
	itembtn5 = types.KeyboardButton('📋Условия программы лояльности')
	markup.add(itembtn1, itembtn2, itembtn3,itembtn4,itembtn5)
	bot.send_message(message.from_user.id, " Выберите из меню:", reply_markup=markup)

"""def birth_date_notifier(message):
	qr_query="SELECT chat_id from clients WHERE chat_id = " + str(user_id) +';'

"""


bot.polling(none_stop=True, interval=0)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)