import string

import telebot
from config import token
import sqlite3
from mat import mat

bot = telebot.TeleBot(token)

with sqlite3.connect("Toxics.db") as db:
    cursor = db.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Toxics(
    ChatID INTEGER,
    ToxicID INTEGER,
    ToxicMetr INTEGER
    )""")
    db.commit()


@bot.message_handler(content_types=['text'])
def text_handler(message):
    # print('text')
    if message.forward_from is None:
        check_mat(message, str(message.text).replace('\n', ' '))


@bot.message_handler(content_types=['photo'])
def photo(photo):
    # print('photo')
    check_mat(photo, photo.caption)


def check_mat(message, text):
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = text.translate(str.maketrans('', '', string.digits))
    text = text.lower()
    text = text.split(' ')
    with sqlite3.connect('Toxics.db') as db:
        cur = db.cursor()
        for word in text:
            if word in mat:
                toxic_metr_from_db = cur.execute(f"""
                    SELECT ToxicMetr FROM Toxics
                    WHERE ChatID={message.chat.id} AND ToxicID={message.from_user.id}
                    """).fetchall()
                if len(toxic_metr_from_db) > 0:
                    toxic_metr = toxic_metr_from_db[0][0]
                    toxic_metr += 1
                    cur.execute(f"""
                        UPDATE Toxics
                        SET ToxicMetr = {toxic_metr}
                        WHERE ChatID={message.chat.id} AND ToxicID={message.from_user.id}
                        """)
                    db.commit()
                else:
                    cur.execute(f"""
                        INSERT INTO Toxics(ChatID, ToxicID, ToxicMetr) VALUES({message.chat.id}, {message.from_user.id}, 1)
                        """)
                    db.commit()
        update_chat_description(message, cur)


def update_chat_description(message, cur):
    chat_description = bot.get_chat(message.chat.id).description
    chat_members = cur.execute(f"""
    SELECT * FROM Toxics
    WHERE ChatID={message.chat.id}
    ORDER BY ToxicMetr DESC
    """).fetchall()
    new_chat_description = 'Топ токсиков в этом чате: \n'
    for i, member in enumerate(chat_members):
        new_chat_description += f'{i + 1}. {bot.get_chat_member(member[0], member[1]).user.username} - {member[2]} раз. повёл себя не культурно;\n'
    new_chat_description = new_chat_description[:-1]
    if chat_description != new_chat_description:
        bot.set_chat_description(message.chat.id, new_chat_description)


bot.infinity_polling()
