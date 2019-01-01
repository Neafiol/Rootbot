import sys
sys.path.append('../')


import sqlite3
import urllib

import bottle
from  bottle import *
import os.path

from Celery import telegram


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

        telegram.tel_sent_quizs(qtext)


    elif (com=='Delete'):
        id = request.POST.get("quizid")

        executebd("""
                           DELETE FROM T_bot_card WHERE id={}
                        """.format(id))
    elif (com=='Distribution'):
        t = rec['name'][0]+':\n'
        t += rec['text'][0]

        telegram.tel_sent_all(t)

    elif (com=='Close'):
        print("Close")
        id = request.POST.get("quizid")
        telegram.tel_sent_docs(id)

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
        telegram.tel_sent_all(ans)



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
    nsub=len(n)

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

run(host='0.0.0.0',port=8080)
