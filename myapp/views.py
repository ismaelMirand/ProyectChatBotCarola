#!/usr/bin/python
# -*- coding: utf-8 -*-
# -*- coding: latin-1 -*-

from datetime import date
import random
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Project, Task
from django.shortcuts import get_object_or_404, render
from . import main
import re
import pyrebase
# Create your views here.

config={
    "apiKey": "AIzaSyDWxYsRq-viVuzpCGajgVCqhBZ39U1Gs1c",
    "authDomain": "chatbotia-8590d.firebaseapp.com",
    "databaseURL": "https://chatbotia-8590d-default-rtdb.firebaseio.com",
    "projectId": "chatbotia-8590d",
    "storageBucket": "chatbotia-8590d.appspot.com",
    "messagingSenderId": "887579188291",
    "appId": "1:887579188291:web:fecfc3bf68fa74ade488f6"
}

firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
database = firebase.database()

conversacion = list()
vote = True
subRespuestaGlobal = ""
preguntasSugeridasGlobal = list()

subRespuesta = [
    "Puede hacerme otra pregunta","¿Necesita saber algo más?","¿Le puedo ayudar con otra cosa?","¿Tiene más dudas? Pregúnteme!"]
respuestaInsulto = [
    "Lo siento pero no voy hablar con alguien que me trata mal, adi\u00f3s",
                "Disculpe pero no voy hablar ni responder dudas con alguien que insulta, adi\u00f3s",
                "Me temo que las palabras que est\u00e1 utilizando no son educadas, me tengo que despedir", 
                "Me ha insultado, no hablaré con usted."]
today = date
saludoInicial = [
    "Hola! Mi nombre es Carola y soy una asistente virtual creada con inteligencia artificial",
    "Hey! Hola! Soy Carola asistente virtual de la carrera ingeniería civil en informática, encargada de ayudar en todo momento a los estudiantes de la universidad del Bío-Bío!",
    "Qué tal! Soy Carola una inteligencia artificial creada para resolver tus dudas!"
    ]
respuestaDespedida = [
    "Adi\u00f3s! Aqu\u00ed le esperar\u00e9 ",
    "Chao! Cuando necesite saber algo pruebe a preguntarme",
    "Aqu\u00ed estar\u00e9 para resolver sus dudas! Hasta la pr\u00f3xima!",
    "Adios! Cu\u00eddese mucho",
    "Gracias por pasar por aqu\u00ed, hasta pronto"]

def index(request):
    channel_name = database.child('prueba').child('nombre').get().val()


    # comentario = "Esto es un comentario"
    # today = date.today()
    # data = {"comentario": comentario, "fecha": str(today)}
    # database.child("comentarios").push(data)

    title = 'Chatbot con Inteligencia Artificial'
    return render(request, 'index.html',{
        'title' : title,
        'nombre': channel_name
    })

def initBot(request):
    global today
    global subRespuestaGlobal
    global preguntasSugeridasGlobal
    global vote

    main.iniciarBot()
    today = date.today()

    respuestaToSave = getRespuesta(random.choice(saludoInicial))
    conversacion.append(respuestaToSave)
    subRes = ""
    preguntasSugeridas = main.getSugerencias()
    
    subRespuestaGlobal = subRes
    preguntasSugeridasGlobal = preguntasSugeridas

    return render(request, "bot.html",{
        'date' : today,
        'conversacion' : conversacion,
        'subpregunta' : subRes,
        'preguntasSugeridas' : preguntasSugeridas,
        'vote' : vote
    })

def enviarComentario(request):
    global today
    comentario = request.POST['pregunta']

    if(comentario == ""):
        return render(request, "bot.html",{
            'date':today,
            'conversacion' : conversacion,
            'subpregunta' : subRespuestaGlobal,
            'preguntasSugeridas' : preguntasSugeridasGlobal,
            'vote' : vote
        })

    today = date.today()
    data = {"comentario": comentario, "fecha": str(today)}
    database.child("comentarios").push(data)

    return render(request, 'comentarioEnviado.html')

def votar(request):
    global vote
    vote = False
    today = date.today()
    pregunta = conversacion[-2].valor
    respuesta = conversacion[-1].primeraParte + conversacion[-1].link + conversacion[-1].segundaParte

    data = {"fecha": str(today), "preguntaEvaluada": pregunta, "respuesta": respuesta}
    database.child("evaluacionPregunta").push(data)

    return render(request, "bot.html",{
        'date':today,
        'conversacion' : conversacion,
        'subpregunta' : subRespuestaGlobal,
        'preguntasSugeridas' : preguntasSugeridasGlobal,
        'vote': vote
    })

def chat(request):
    return render(request, "bot.html",{
        'date':today,
        'conversacion' : conversacion,
        'subpregunta' : subRespuestaGlobal,
        'preguntasSugeridas' : preguntasSugeridasGlobal,
        'vote' : vote
    })


def documentacion(request):
    return render(request, 'documentacion.html')

def comentario(request):
    return render(request, 'comentario.html')

# def comentarioEnviado(request):
#     return render(request, 'comentarioEnviado.html')

def preguntar(request):
    global today
    global subRespuestaGlobal
    global preguntasSugeridasGlobal
    global vote
    vote = True

    pregunta = request.POST['pregunta']

    if(pregunta != ""):
     
        respuestaDelBot = main.response(pregunta)
        
        preguntaToSave = Pregunta('pregunta', pregunta)
        respuestaToSave = getRespuesta(respuestaDelBot.respuesta);

        conversacion.append(preguntaToSave)
        conversacion.append(respuestaToSave)

        # print(">>> respuestaDelBot.respuesta", respuestaDelBot.respuesta)

        if(respuestaDelBot.respuesta == "Lo siento, creo que no tengo esa información, de todas maneras puede intentar reformular su pregunta"):
            today = date.today()
            pregunta = preguntaToSave.valor
            data = {"fecha": str(today), "pregunta": pregunta }
            database.child("preguntasNoEncontradas").push(data)
            vote = False

        if (respuestaDelBot.respuesta in respuestaInsulto) or (respuestaDelBot.respuesta in respuestaDespedida):
            subRes = ""
            respuestaDelBot.preguntasSugeridas = []
            vote = False

        else:
            subRes = random.choice(subRespuesta)

        subRespuestaGlobal = subRes
        preguntasSugeridasGlobal = respuestaDelBot.preguntasSugeridas

        return render(request, "bot.html",{
            'date':today,
            'conversacion' : conversacion,
            'subpregunta' : subRes,
            'preguntasSugeridas' : respuestaDelBot.preguntasSugeridas,
            'vote' : vote
        })

    return render(request, "bot.html",{
        'date':today,
        'conversacion' : conversacion,
        'subpregunta' : subRespuestaGlobal,
        'preguntasSugeridas' : preguntasSugeridasGlobal,
        'vote' : vote
    })

def getRespuesta(mensajeBot):
    hayLink = mensajeBot.find("http");
    if hayLink!=-1:
        tipoLink = "url"

    else:
        hayLink = mensajeBot.find("@");
        tipoLink = "email"

    if (hayLink!=-1):
        url = encontrarLink(mensajeBot)[0]
        ubiLink = mensajeBot.find(url)

        primeraParte = mensajeBot[0:ubiLink]
        
        segundaParte = mensajeBot[(len(primeraParte)+len(url)):len(mensajeBot)]

        return Respuesta("respuesta",primeraParte,tipoLink, url ,segundaParte)

    else:
        return Respuesta("respuesta",mensajeBot,"","","");

def encontrarLink(texto):   
    exprRegParaURL = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(exprRegParaURL, texto)

    if len(url)<1:
        exprRegParaCorreo = r"[a-zA-Z0-0._%+-]+@[a-z0-9.-]+.[a-z]{2,}"
        correos = re.findall(exprRegParaCorreo, texto)

        print(">>>> len(correos)", len(correos))
        print(">>>>> correo en correos", correos[0])
        return correos
    else: 
        return url[0]

class Pregunta:
    tipo = ""
    valor = ""

    def __init__(self, tipo, valor):
        self.tipo = tipo
        self.valor = valor
    
    def setTipo(self, tipo):
        self.tipo = tipo;
    
    def setValor(self, valor):
        self.valor = valor;

    def getTipo(self):
        return self.tipo

    def getValor(self):
        return self.valor

class Respuesta:
    tipo = ""
    primeraParte = ""
    tipoLink = ""
    link = ""
    segundaParte = ""

    def __init__(self, tipo, primeraParte,tipoLink,link,segundaParte):
        self.tipo = tipo
        self.primeraParte = primeraParte
        self.tipoLink = tipoLink
        self.link = link
        self.segundaParte = segundaParte
    
    def setTipo(self, tipo):
        self.tipo = tipo;
    
    def setValor(self, valor):
        self.valor = valor;

    def getTipo(self):
        return self.tipo

    def getValor(self):
        return self.valor

