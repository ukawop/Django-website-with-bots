from django.urls import path, include

from . import views



urlpatterns = [
    path('bot<str:bot_token>/message/<int:id>', views.MessageIDView.as_view()),
    path('bot<str:bot_token>/message/getUpdates/', views.MessageGetUpdatesView.as_view()),
    path('bot<str:bot_token>/message/botLast/', views.MessageBotLastView.as_view()),
    path('bot<str:bot_token>/message/everyLast/', views.MessageEveryLastInfoView.as_view()),
    path('bot<str:bot_token>/message/sendText/', views.MessageSendTextView.as_view()),
    path('bot<str:bot_token>/message/sendImage/', views.MessageSendImageView.as_view()),
    path('bot<str:bot_token>/media/<str:path>', views.TakeImageView.as_view()),
]