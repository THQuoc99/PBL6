from django.urls import path
from . import views
from django.shortcuts import render

urlpatterns = [
    path('chat/', views.chat_with_gpt, name='chat_with_gpt'),
]

