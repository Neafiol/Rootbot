import sys
sys.path.append('../')


import sqlite3
import urllib

import bottle
from  bottle import *
import os.path

import os
import sqlite3


import telebot
from PIL import Image
from fpdf import FPDF
from  telebot import types
token = '631463430:AAFK6pH4qDhEupWb4HdM0ICLG-0rDhUGIlg'

start_text="""
    Проивет, рад тебя видеть, добро пожаловать в клуб фтл гдз!
    Поздравляю, теперь ты можешь больше не боспокоится о бесполезных предметах)
    Правила клуба просты:
    1 правило. Никому не говорить о клубе
    2 правило. Никому не говорить о клубе
    3 правило. Прилетел вопрос от бота - ответь и знай: скоро прилетит очередная сделанная дз
    4 правило. Информатика - это святое, на нее нет гдз
    5 правило. Слитыми тут дз не делится!
    6 правило. Когда закончил выполнение дз, нажми на кнопку Done.
    7 правило. Отправлять можно только текс или фото
    Успехов тебе и трать время с умом, а бонусом сюда будут прилетать уведомдения об олимпиадках)
"""
restart_text="""
    Ты уже с нами, дебил!
"""

bot = telebot.TeleBot(token)

#status message:
#0 - wait quiz
#1 - thinhing
#2 - making
def executebd(c):
    try:
        print(c)
        conn = sqlite3.connect("../db.sqlite3")  # или :memory: чтобы сохранить в RAM
        db = conn.cursor()
        db.execute(c)
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)

def tel_sent_all(text):
    conn = sqlite3.connect("../db.sqlite3")  # или :memory: чтобы сохранить в RAM
    db = conn.cursor()
    subs = db.execute("""
                           SELECT `tel_id` FROM T_bot_subscriber WHERE status_message=0
                        """).fetchall()
    conn.commit()
    conn.close()
    for s in subs:
        bot.send_message(s[0], text)
    return True
#
def tel_sent_docs(id):
    pdf = FPDF()

    path = r"..\files\photos\{}".format(id)
    try:
        imagelist = os.listdir(path)
        # imagelist is the list with all image filenames
        for image in imagelist:
            if image.find('.pdf'):
                continue
            cover = Image.open(path + '\\' + image)
            width, height = cover.size
            pdf.add_page()
            pdf.image(path + '\\' + image, 10, 10, min(width / 5, 206), min(height / 5, 290))
        pdf.output(path + '\\'"ans.pdf", "F")

        conn = sqlite3.connect("../db.sqlite3")  # или :memory: чтобы сохранить в RAM
        db = conn.cursor()
        subs = db.execute("""
                               SELECT `tel_id` FROM T_bot_subscriber WHERE status_message=0
                            """).fetchall()
        conn.commit()
        conn.close()

        for s in subs:
            doc = open(path + '\\'"ans.pdf", 'rb')
            bot.send_document(s[0], doc)

    except Exception as e:
        print(e)
    return True


def tel_sent_quizs(text):
    st = text.split(';')

    conn = sqlite3.connect("../db.sqlite3")  # или :memory: чтобы сохранить в RAM
    db = conn.cursor()
    subs = db.execute("""
                       SELECT `tel_id` FROM T_bot_subscriber WHERE status_message=0
                    """).fetchall()
    qid=db.execute("""
                       SELECT MAX(id)  FROM T_bot_card
                    """).fetchall()[0][0]
    quiz = db.execute("""
                           SELECT MAX(id)  FROM T_bot_question
                        """).fetchall()[0][0]
    conn.commit()
    conn.close()

    i=0
    for s in subs:
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text='Done', callback_data='/done')
        button.OneTimeKeyboard = True
        markup.add(button)

        bot.send_message(s[0], st[i], reply_markup=markup)
        executebd("""
                    INSERT INTO T_bot_question (`qstID`,`text`,`subsID`,answer) VALUES({},'{}',{},' ')
                """.format(qid, st[i], s[0]))

        executebd("""
            UPDATE T_bot_subscriber SET  status_message=1, quis_now={} WHERE `tel_id`={}
        """.format(quiz+i,s[0]))
        i+=1

    return 0


def executebd(c):
    try:
        conn = sqlite3.connect("../db.sqlite3")  # или :memory: чтобы сохранить в RAM
        db = conn.cursor()
        db.execute(c)
        conn.commit()
        conn.close()
    except:
        1





@post("/quiz_red")
def close_qst():
    rec = urllib.parse.parse_qs(request.body.read().decode())

    com=request.POST.get("action")
    if(com=='Add Quiz'):
        qname = rec['name'][0]
        qtext = rec['text'][0]

        executebd("""
                            INSERT INTO T_bot_card  (`name`) VALUES('{}')
                        """.format(qname))

        tel_sent_quizs(qtext)


    elif (com=='Delete'):
        id = request.POST.get("quizid")

        executebd("""
                           DELETE FROM T_bot_card WHERE id={}
                        """.format(id))
    elif (com=='Distribution'):
        t = rec['name'][0]
        t += rec['text'][0]

        tel_sent_all(t)

    elif (com=='Close'):
        print("Close")
        id = request.POST.get("quizid")
        tel_sent_docs(id)

        conn = sqlite3.connect("../db.sqlite3")  # или :memory: чтобы сохранить в RAM
        db = conn.cursor()
        # добавим в базу
        ans = db.execute("""
                               SELECT `name` FROM T_bot_card WHERE id={}
                            """.format(id)).fetchall()[0][0] + '\n'
        db.execute("""
                               UPDATE T_bot_subscriber SET  status_message={} WHERE quis_now={}
                            """.format(0,id))

        for t in db.execute("""
                                   SELECT `text`,`answer` FROM T_bot_question WHERE qstID={}
                                """.format(id)).fetchall():
            ans += t[0] + ' : ' + t[1] + '\n'
        db.execute("""
                                   DELETE FROM T_bot_question WHERE qstID={}
                                """.format(id))
        db.execute("""
                                       DELETE FROM T_bot_card WHERE id={}
                                    """.format(id))
        conn.commit()
        conn.close()
        tel_sent_all(ans)



    return redirect('/')

@get("<filepath:re:.*\.css>")
def css(filepath):
    return static_file(filepath, root="static/css")
@get("<filepath:re:.*\.js>")
def js(filepath):
    return static_file(filepath, root="static/js")

@route('/')
def index():
    conn = sqlite3.connect("../db.sqlite3")  # или :memory: чтобы сохранить в RAM
    db = conn.cursor()
    data = db.execute("""
                       SELECT * FROM T_bot_card 
                    """.format(id)).fetchall()
    n = db.execute("""
                       SELECT * FROM T_bot_subscriber WHERE status_message={}
                    """.format(0)).fetchall()
    nsub=len(n);

    conn.commit()
    conn.close()
    if(len(data)>0):
    # print(data['id'])
        return template( 'index.html' ,  subscount=nsub,cards= data)
    else:
        return template('index.html',subscount=nsub,cards=[[0,0]])

@route('/<name:re:[0-9]*>')
def show_news(name):
    return template('data.html')

    pass

run(host='0.0.0.0', port=8080)