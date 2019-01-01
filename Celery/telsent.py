# -*- coding: utf-8 -*-
from Celery import config
import telebot
from  telebot import types
import sqlite3
import sys
import os
from fpdf import FPDF
#from T_bot.models import Subscriber
def log(txt):
    file = open("../log.txt", "a")
    file.write(txt+'\n')
    file.close()
    bot.send_message(445330281,"11B_Logs: " + txt)

bot = telebot.TeleBot(config.token)



@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    try:
        conn = sqlite3.connect("../db.sqlite3")  # или :memory: чтобы сохранить в RAM
        db = conn.cursor()
        # добавим в базу
        qn = db.execute("""
               SELECT quis_now FROM T_bot_subscriber WHERE tel_id={}
            """.format(message.chat.id)).fetchall()[0][0]

        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        path="../files/photos/"+str(qn)
        if not os.path.exists(path):
            os.makedirs(path)

        out = open(path+'/'+str(message.chat.id+message.message_id)+'.jpg', "wb")

        out.write(downloaded_file)
        out.close()
        print("Новое фото",message.message_id)
        log("Добавлено фото:" +str(message.from_user.last_name))
        bot.reply_to(message, "Фото добавлено")

    except Exception as e:
        bot.reply_to(message, e)

@bot.message_handler(commands=['admin_'])
def repeat_all_messages(message): # Название функции не играет никакой роли, в принципе
    print(message.chat.id)
    log("Стал админом :" + str(message.from_user.last_name))
    bot.send_message(message.chat.id, "Получены права суперпользователя")

@bot.message_handler(commands=['start'])
def repeat_all_messages(message): # Название функции не играет никакой роли, в принципе

    conn = sqlite3.connect("../db.sqlite3")  # или :memory: чтобы сохранить в RAM
    db = conn.cursor()
    #добавим в базу
    now=db.execute("""
       SELECT * FROM T_bot_subscriber WHERE tel_id={}
    """.format(message.chat.id)).fetchall()

    if(len(now)==0):
        name=str(message.from_user.first_name) +'_'+ str(message.from_user.last_name)
        db.execute("""
            INSERT INTO T_bot_subscriber  (tel_id, `name` ,status_message, rating) VALUES({},'{}',0,5)
        """.format(str(message.chat.id) , name ))
        bot.send_message(message.chat.id, config.start_text)
    else:
        bot.send_message(message.chat.id, config.restart_text)
    conn.commit()
    conn.close()
    print("enter: ", message.chat.id)

    log("Присоеденился:" + str(message.from_user.last_name))



@bot.message_handler(commands=['goout'])
def repeat_all_messages(message): # Название функции не играет никакой роли, в принципе
    conn = sqlite3.connect("../db.sqlite3")  # или :memory: чтобы сохранить в RAM
    db = conn.cursor()
    # добавим в базу
    db.execute("""
           DELETE FROM T_bot_subscriber WHERE tel_id={}
        """.format(message.chat.id))
    conn.commit()
    conn.close()

    print("drop: ",message.chat.id)
   # Subscriber().objects.filter(telid=message.chat.id).delete()
    bot.send_message(message.chat.id, "Прощай, бро")
    log("Ушел:" + str(message.from_user.last_name))

@bot.callback_query_handler(func=lambda call: True)
def repeat_all_messages(call):

    conn = sqlite3.connect("../db.sqlite3")  # или :memory: чтобы сохранить в RAM
    db = conn.cursor()
    if call.from_user:
        if call.data == "/done":
            db.execute("""
                               UPDATE T_bot_subscriber SET  status_message=0 WHERE `tel_id`={}
                            """.format(call.from_user.id))

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Вопрос закрыт")
            bot.send_message(chat_id=call.message.chat.id, text="Вопрос закрыт")
            log("Закрыл вопрос:" + call.from_user.last_name)
    conn.commit()
    conn.close()


@bot.message_handler(content_types=["text"])
#обработка ответа от участника
def repeat_all_messages(message):
    conn = sqlite3.connect("../db.sqlite3")  # или :memory: чтобы сохранить в RAM
    db = conn.cursor()
    print(str(message.from_user.last_name)+' : '+message.text)
    # добавим в базу
    if(db.execute("""
       SELECT status_message FROM T_bot_subscriber WHERE id={}
        """.format(message.chat.id))==0):
        bot.send_message(message.chat.id, "Нет активных вопросов")
        return
    try:
        ans= db.execute("""
       SELECT answer FROM T_bot_question WHERE subsID={}
        """.format(message.chat.id)).fetchall()

        db.execute("""
                   UPDATE T_bot_question SET  answer="{}" WHERE `subsID`={}
                """.format(ans[0][0]+'-'+message.text,message.chat.id))

        bot.send_message(message.chat.id, "Твой ответ добавлен, спс")
    except Exception as e:
        bot.send_message(message.chat.id, "Нет активного вопроса")
        print(e)
    conn.commit()
    conn.close()
    log(str(message.from_user.last_name)+' : '+message.text)


if __name__ == '__main__':
    #bot.send_message(445330281, "123")
    try:
        bot.polling(none_stop=True)
    except:
        print("Error")
        bot.polling(none_stop=True)