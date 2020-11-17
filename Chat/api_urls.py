from django.urls import path

from Chat import views

app_name = 'chat'

urlpatterns = [
    path(r'chat/<uuid:chat_uuid>/messages', views.fetch_messages),
    path(r'chat/<uuid:chat_uuid>/send', views.send_message)
]
