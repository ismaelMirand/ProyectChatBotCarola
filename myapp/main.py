#!/usr/bin/python
# -*- coding: utf-8 -*-
# -*- coding: latin-1 -*-
#LIBRERIAS

from unittest import result
from xml.dom.minidom import Document
import nltk
nltk.download("punkt")

from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()
import re 
import numpy
import tflearn
import tensorflow
from tensorflow.python.framework import ops
import json
import random
import pickle 
import requests
import os 
import matplotlib as mltp
import dload
import itertools

print ("Librerías OK")

words=[]
all_words=[]
tags=[]
aux=[]
auxA=[]
auxB=[]
training=[]
exit=[]
dataBaseAux=any

state = True
limiteSuperior = any
limiteInferior = any

#dload.git_clone("https://github.com/boomcrash/data_bot.git")
def iniciarBot(): 
    global words
    global all_words
    global tags
    global aux
    global auxA
    global auxB
    global training
    global exit

    print("Iniciando Bot...")
    dir_path=os.path.dirname(os.path.realpath(__file__))
    dir_path=dir_path.replace("\\","//")
    with open(dir_path+'/data_bot\data_bot-main/data.json','r') as file:
            global database
            database=json.load(file)

    print("PATH -> ", os.path.dirname(os.path.realpath(__file__)))
    print ("PATH 2 -> ", dir_path)
    
    try:
        print("intentando Abrir brain.pickle si es que existe")
        with open("training/brain.pickle","rb") as pickleBrain:
            all_words,tags,training,exit=pickle.load(pickleBrain)
        print("Ya no hice el except, porque todo están en brain.pickle")
    except:
        print("No existe brain.pickle así que lo crearemos")
        for intent in database["intents"]:
            for pattern in intent["patterns"]:
                #separamos la frase en palabras
                auxWords=nltk.word_tokenize(pattern)
                #guardamos las palabras
                auxA.append(auxWords)
                auxB.append(auxWords)
                #guardar lo tags
                aux.append(intent["tag"])
        #simbolos a ignorar
        ignore_words=['?','!','.',',','¿',"'",'"','$','-',':','_','&','%','/','(',')','=','*','#']
        for w in auxB:
            if w not in ignore_words:
                words.append(w)
        words=sorted(set(list(itertools.chain.from_iterable(words))))
        # print(words)

        tags=sorted(set(aux))
        # print(tags)

        #convertir a minuscula
        all_words=[stemmer.stem(w.lower()) for w in words]
        print(len(all_words))

        all_words=sorted(list(set(all_words)))

        #ordenar tags
        tags=sorted(tags)
        training=[]
        exit=[]
        #creamos una salida falsa
        null_exit=[0 for _ in range(len(tags))]
        print(null_exit)

        for i,document in enumerate(auxA):
            bucket=[]
            #minuscula y quitar signos
            auxWords=[stemmer.stem(w.lower()) for w in document if w!="?"]
            "recorremos"
            for w in all_words:
                if w in auxWords:
                    bucket.append(1)
                else:
                    bucket.append(0)
            exit_row=null_exit[:]
            exit_row[tags.index(aux[i])]=1
            training.append(bucket)
            exit.append(exit_row)

        training=numpy.array(training)
        #print(training)
        exit=numpy.array(exit)

        #crear archivo pickle 
        with open("training/brain.pickle","wb") as pickleBrain:
            pickle.dump((all_words,tags,training,exit),pickleBrain)

    
    tensorflow.compat.v1.reset_default_graph()
    tflearn.init_graph()
    #creamos la red neuronal
    net=tflearn.input_data(shape=[None,len(training[0])])
    #redes intermedias
    net=tflearn.fully_connected(net,100,activation='Relu')
    net=tflearn.fully_connected(net,50)
    net=tflearn.dropout(net,0.5)
    #Salida
    net=tflearn.fully_connected(net,len(exit[0]), activation='softmax')
    #red completada
    net=tflearn.regression(net, optimizer='adam',learning_rate=0.01,loss='categorical_crossentropy')
    global model
    model = tflearn.DNN(net)

    if os.path.isfile("D:/chatbotIA/training/model.tflearn.index"):
        model.load("D:/chatbotIA/training/model.tflearn")
        print("ya existe datos entrenados")
    else:
        model.fit(training,exit,validation_set=0.1,show_metric=True,batch_size=128, n_epoch=2000)
        model.save("D:/chatbotIA/training/model.tflearn")
    establecerLimites()

def response(texto):
    global state
    global model
    global database
    global tags

    indexPregunta = 0

    bucket=[0 for _ in range(len(all_words))]
    processed_sentence=nltk.word_tokenize(texto)
    processed_sentence=[stemmer.stem(palabra.lower()) for palabra in processed_sentence]
    for individual_word in processed_sentence:
        for i,palabra in enumerate(all_words):
            if palabra==individual_word:
                bucket[i]=1
    
    results=model.predict([numpy.array(bucket)])
    index_results=numpy.argmax(results)
    max=results[0][index_results]
    target=tags[index_results]
    
    #TODO: IMPLEMENTAR DESCONOCIMIENTO DE INFORMACION
    #CREO QUE CON LA VARIABLE MAX ES POSIBLE HACERLO!

    print(">>> max", max)

    if state and max < 0.21:
        pS =[];
        return AnswerBot("Lo siento, creo que no tengo esa información, de todas maneras puede intentar reformular su pregunta", pS)

    if target == "disculpas":
        state = True

    if not state:
        sinSugrencias = []
        return AnswerBot("Me ha insultado, no hablaré con usted.", sinSugrencias)

    # print("database['intents']")
    # print(database["intents"][0])

    for index, tagAux in enumerate(database["intents"]):
        # print("index ->", index)
        if tagAux['tag']==target:
            answer=tagAux['responses']
            answer=random.choice(answer)
            # print(" > index ganador ->", index);
            indexPregunta = index

            # print(">>>>> target", target)

            if target == "insultos":
                state = False

    preguntasSugeridas = getSugerenciasByIndex(indexPregunta)

    return AnswerBot(answer, preguntasSugeridas)

def getSugerencias():
    global database
    global limiteInferior
    global limiteSuperior

    indexP1 = random.randint(limiteInferior+1, limiteSuperior-1)
    indexP2 = random.randint(limiteInferior+1, limiteSuperior-1)

    # print(">> indexP1", indexP1)
    # print(">> indexP2", indexP2)

    preguntasSugeridas = list()
    preguntasSugeridas.append(database["intents"][(indexP1)]['patterns'][0])
    preguntasSugeridas.append(database["intents"][(indexP2)]['patterns'][0])

    return preguntasSugeridas

def getSugerenciasByIndex(index):
    global database
    global limiteInferior
    global limiteSuperior

    # print("> index", index);

    if index <= limiteInferior:
        indexP1 = limiteInferior+1
        indexP2 = limiteInferior+2

    else:
        indexP1 = index + (random.randint(1, 2))
        indexP2 = index - (random.randint(1, 2))

        # print("if", indexP1, ">", limiteSuperior)
        if indexP1 > limiteSuperior:
            indexP1 = indexP2 - 1;

        # print("if", indexP2, "<", limiteInferior)
        if indexP2 < limiteInferior:
            indexP2 = indexP1 + 1;

    # print("> indexP1", indexP1);
    # print("> indexP2", indexP2);

    preguntasSugeridas = list()
    preguntasSugeridas.append(database["intents"][(indexP1)]['patterns'][0])
    preguntasSugeridas.append(database["intents"][(indexP2)]['patterns'][0])

    return preguntasSugeridas

def establecerLimites():
    global database
    global limiteInferior
    global limiteSuperior

    for index, tagAux in enumerate(database["intents"]):
        if tagAux['tag']=="numero de ramos":
            limiteInferior=index
            print(">>>>> limiteInferior", limiteInferior)

        if tagAux['tag']=="plazoproyectodetituloingenieriacivilinformatica":
            limiteSuperior=index
            print(">>>>> limiteSuperior", limiteSuperior)

class AnswerBot:
    respuesta = ""
    preguntasSugeridas = []

    def __init__(self, respuesta, preguntasSugeridas):
        self.respuesta = respuesta
        self.preguntasSugeridas = preguntasSugeridas
    

