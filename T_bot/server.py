import os

from PIL import Image
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from fpdf import FPDF

from T_bot.models import Question
from T_bot.models import Subscriber
from T_bot.models import Card
from Celery import telegram

def create(request):
    if request.method == "POST":
        text = request.POST.get("text")
        st = text.split(';')

        cd = Card()
        cd.name = request.POST.get("name")
        cd.date = request.POST.get("date")
        cd.save()
        try:
            id = Card.objects.latest('id').id
            for s in st:
                if (s != ''):
                    qv = Question()
                    qv.text = s
                    qv.qstID = id
                    qv.subsID = 0
                    qv.answer = ""
                    qv.save()
        except:
            1
        telegram.tel_sent_quizs(id)

def drop(request):
    if request.method == "POST":
        id = int( request.POST.get("id"))
        Card.objects.filter(id=id).delete()
        try:
            st=Question.objects.filter(qstID=id)
            for s in st:
                s.delete()
        except:
            1
def cmd(request):
    if request.method == "POST":
        if(request.POST.get("cmd")=='send_all'):
            text=request.POST.get("text")
            telegram.tel_sent_all(text)
            return True

        if(request.POST.get("cmd")=='close_qst'):
            id=request.POST.get("id")
            telegram.tel_sent_docs(id)


            answ=Card.objects.filter(id=id)[0].name+'\n'
            for s in Subscriber.objects.filter(quis_now=id):
                s.status_message=0
                s.save()

            for s in Question.objects.filter(qstID=id):
                answ+=s.text+' : '+s.answer+'\n'
                s.delete()
            Card.objects.filter(id=id).delete()
            print("sendt to all: ",answ)
            telegram.tel_sent_all(answ)
            return True

