from django.contrib import admin

from Chat.models.chat_room import ChatRoom
from Chat.models.message import Message
from Chat.models.participant import Participant
from Chat.models.unread_message import UnreadMessage

admin.site.register(ChatRoom)
admin.site.register(Message)
admin.site.register(Participant)
admin.site.register(UnreadMessage)
