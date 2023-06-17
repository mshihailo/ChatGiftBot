import sqlite3

conn = sqlite3.connect('gifts.db')
cursor = conn.cursor()

# создаем таблицу gifts
cursor.execute('''CREATE TABLE gifts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  description TEXT,
                  price REAL,
                  link TEXT)''')

# добавляем несколько записей в таблицу gifts
cursor.execute("INSERT INTO gifts (name, description, price, link) VALUES ('Футболка', 'Мужская футболка Nike', 2000, 'https://example.com/gift1')")
cursor.execute("INSERT INTO gifts (name, description, price, link) VALUES ('Часы', 'Мужские часы Casio', 5000, 'https://example.com/gift2')")
cursor.execute("INSERT INTO gifts (name, description, price, link) VALUES ('Кофемашина', 'Домашняя кофемашина DeLonghi', 10000, 'https://example.com/gift3')")

conn.commit()
conn.close()
