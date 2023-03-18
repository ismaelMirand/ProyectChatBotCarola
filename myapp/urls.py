from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('iniciarBot/', views.initBot, name='iniciarBot'),
    path('preguntar/', views.preguntar),
    path('votar/', views.votar, name='votar'),
    path('documentacion/', views.documentacion, name='documentacion'),
    path('comentario/', views.comentario, name='comentario'),
    path('chat/', views.chat, name='chat'),
    path('enviarComentario/', views.enviarComentario),


]