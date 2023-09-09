import string

import telebot
from config import token
from config import admin_id
import sqlite3
from mat import mat

bot = telebot.TeleBot(token)
mat_words = mat

with sqlite3.connect("Toxics.db") as db:
    cursor = db.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Toxics(
    ChatID INTEGER,
    ToxicID INTEGER,
    ToxicMetr INTEGER
    )""")
    db.commit()


@bot.message_handler(commands=['get_db'])
def get_words(message_info):
    if message_info.from_user.id == admin_id:
        with open("Toxics.db", "rb") as file:
            bot.send_document(message_info.chat.id, file)


@bot.message_handler(commands=['get_sw'])
def get_words(message_info):
    if message_info.from_user.id == admin_id:
        with open("mat.py", "rb") as file:
            bot.send_document(message_info.chat.id, file)


@bot.message_handler(commands=['add'])
def add_words(add_words):
    global mat_words
    if add_words.from_user.id == admin_id:
        # print('add')
        text = add_words.text[5:]
        if text != '':
            text = text.replace('\n', ' ')
            text = text.translate(str.maketrans('', '', string.punctuation))
            text = text.translate(str.maketrans('', '', string.digits))
            text = text.lower()
            text = text.replace('  ', ' ')
            words = text.split(' ')
            words = [word for word in words if word != '']
            words = list(set(words))
            for word in words:
                if word in mat_words:
                    words.remove(word)
            if len(words) > 0:
                mat_words += words
                mat_words.sort()
                with open('mat.py', 'w', encoding='utf-8') as file:
                    file.write(f'mat = {mat_words}')
                add_mat = str(words).strip("[]").replace("'", '').replace(', ', ';\n')
                bot.send_message(add_words.chat.id, f'Слова:\n{add_mat}\nуспешно добавлены.')


@bot.message_handler(commands=['delete'])
def delete_words(delete_words):
    global mat_words
    if delete_words.from_user.id == 790804074:
        # print('delete')
        text = delete_words.text[8:]
        if text != '':
            text = text.replace('\n', ' ')
            text = text.translate(str.maketrans('', '', string.punctuation))
            text = text.translate(str.maketrans('', '', string.digits))
            text = text.lower()
            text = text.replace('  ', ' ')
            words = text.split(' ')
            words = [word for word in words if word != '']
            for word in words:
                if word in mat_words:
                    mat_words.remove(word)
                else:
                    words.remove(word)
            if len(words) > 0:
                mat_words.sort()
                with open('mat.py', 'w', encoding='utf-8') as file:
                    file.write(f'mat = {mat_words}')
                remove_mat = str(words).strip("[]").replace("'", '').replace(', ', ';\n')
                bot.send_message(delete_words.chat.id, f'Слова:\n{remove_mat}\nуспешно удалены.')


@bot.message_handler(chat_types=['group', 'supergroup', 'channel'], content_types=['text'])
def text_handler(message):
    # print('text')
    check_mat(message, message.text)


@bot.message_handler(chat_types=['group', 'supergroup', 'channel'], content_types=['photo'])
def photo_handler(message):
    # print('photo')
    check_mat(message, message.caption)


def check_mat(message, text):
    if message.forward_from is None and (message.text is not None or message.caption is not None) and text != '':
        text = text.replace('\n', ' ')
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = text.translate(str.maketrans('', '', string.digits))
        text = text.lower()
        words = text.split(' ')
        with sqlite3.connect('Toxics.db') as db:
            cur = db.cursor()
            for word in words:
                if word in mat_words:
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
                            INSERT INTO Toxics(ChatID, ToxicID, ToxicMetr)
                            VALUES({message.chat.id}, {message.from_user.id}, 1)
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
    new_chat_description = 'Топ токсиков в этом чате(кол-во оскорблений):\n'
    for i, member in enumerate(chat_members):
        toxic = bot.get_chat_member(member[0], member[1]).user.username
        if toxic is not None:
            toxic = f'@{toxic}'
        elif toxic is None:
            toxic_f_name = bot.get_chat_member(member[0], member[1]).user.first_name
            toxic_l_name = bot.get_chat_member(member[0], member[1]).user.last_name
            toxic = ''
            if toxic_f_name is not None:
                toxic += toxic_f_name
            if toxic_l_name is not None:
                toxic += toxic_l_name
        toxic_info = f'{i + 1}. {toxic} - {member[2]};\n'
        if len(new_chat_description + toxic_info) < 255:
            new_chat_description += toxic_info
        else:
            break
    new_chat_description = new_chat_description[:-1]
    if chat_description != new_chat_description:
        try:
            bot.set_chat_description(message.chat.id, new_chat_description)
        except telebot.apihelper.ApiTelegramException as e:
            # print(e)
            if str(e).find('not enough rights to set chat description') != -1:
                bot.send_message(message.chat.id, 'Мне нужны права администратора')


bot.infinity_polling()
