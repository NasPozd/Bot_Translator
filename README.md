**Python translator bot**
========================
## Бот-переоводчик на python

"My teacher Richard" - это Telegram бот-переводчик с английского языка на русский и обратно. Бот предназначен для тех, кто хочет улучшить свой уровень английского языка, общаться с носителями языка и получать помощь в переводе текстов. Он работает на основе библиотеки Google Translate API и обеспечивает высокую точность и скорость перевода. Бот также может присылать уведомления с напоимнаниями об изученных словах.
### Требования
#### Версия Python
Python 3.7+
#### Библиотеки
aiogram - ```pip install aiogram```

mysql-connector-python - ```pip install mysql-connector-python```

google_trans_new - ```google-trans-new```

threaded - ```pip install threaded```

asyncio - ```pip install asyncio```

nest-asyncio - ```pip install nest-asyncio```

### Команды бота
/start Начало работы с ботом(создание клавиатуры для работы)

Просто Ввод соощебния - бот переведет его

### Config.py
TOKEN - токен вашего телеграм бота

STARTMSG - сообщение при /start

db_config - данные бд

### words.py

en - Фраза на EN

ru - Фраза на RU

(у фразы в en и её перевода в ru, должны быть одинаковые индексы)

### work_with_bd.py - модуль для работы с БД

mysql

создать таблицу

def create_connection_mysql_db(db_host, user_name, user_password, db_name = None):
	connection_db = None
        try:
        	connection_db = mysql.connector.connect(
                    host = db_host,
                    user = user_name,
                    passwd = user_password,
                    database = db_name
                    )
                
        except Error as db_connection_error: print("Возникла ошибка: ", db_connection_error)
        return connection_db
conn = create_connection_mysql_db(db_config["mysql"]["host"], db_config["mysql"]["user"], db_config["mysql"]["pass"], 					  		  db_config["mysql"]["database"]) 
cursor = conn.cursor()
table = '''CREATE TABLE user_data (
 		id BIGINT(100) NOT NULL,
 		list_words LONGTEXT NULL,
 		notifications_status INT NULL,
 		notifications_time MEDIUMTEXTNULL,
 		PRIMARY KEY (id)) ENGINE = InnoDB'''
cursor.execute(table)
conn.commit(); cursor.close(); conn.close()

