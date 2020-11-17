import uuid

from django.db import models

from django.db.models import Subquery
from django.db.models.functions import Now

from Chat.models.participant import Participant
from Chat.models.unread_message import UnreadMessage
from django.contrib.auth.models import User



class MessageQuerySet(models.query.QuerySet):
    def messages_before_message(self, message_uuid: str):
        """Returns messages with a date LESS than the date of the selected message"""
        date = Message.objects.get_message_date(message_uuid)
        return self.filter(date__lt=Subquery(date))


class MessageManager(models.Manager):
    def get_queryset(self):
        """Returns custom QuerySet"""
        return MessageQuerySet(self.model)

    def read_messages(self, chat_uuid: str, user_id: int):
        """Returns READ messages from newest to oldest"""
        return (
            self.get_queryset()
            .filter(chat_room=chat_uuid)
            .exclude(unreadmessage__participant__person=user_id))

    def unread_messages(self, chat_uuid: str, user_id: int):
        """Returns UNREAD messages from oldest to newest"""
        return (
            self.get_queryset()
            .filter(
                chat_room=chat_uuid,
                unreadmessage__participant__person=user_id)
            .reverse())

    def get_message_date(self, message_uuid: str):
        """Returns the date of the selected message"""
        return self.get_queryset().filter(id=message_uuid).values_list('date', flat=True)[:1]


class Message(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    chat_room = models.ForeignKey('Chat.ChatRoom', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=False, max_length=255)
    date = models.DateTimeField(default=Now)
    objects = MessageManager()

    class Meta:
        db_table = 'message'
        ordering = ('-date',)

    def save(self, *args, **kwargs):
        participants = (
            Participant.objects
            .filter(chat_room=self.chat_room_id)
            .exclude(person=self.sender_id))
        UnreadMessage.objects.bulk_create([
            UnreadMessage(message=self, participant=p)
            for p in participants])
        super().save(*args, **kwargs)
