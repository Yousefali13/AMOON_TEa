from django.urls import path
from .views import messages_list, chat_view

app_name = 'chat'  

urlpatterns = [
    path('messages/', messages_list, name='messages'),
    path('messages/<int:user_id>/', chat_view, name='chat'),  
]
