import uuid

from django.db import models

from Chat.models.message import Message
from Chat.utils.helpers import preprocess_count
from Chat.utils.validators import validate_message_text, validate_messages_type


class ChatRoom(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'chat_room'
        ordering = ('name',)

    @classmethod
    def get_messages(
            cls,
            chat_uuid: str,
            user_id: int,
            messages_type: str = None,
            count: str = None,
            message_uuid: str = None) -> list:
        """
        Returns the messages from the database

        Parameters
        ----------
        chat_uuid: str
            the primary key of the ChatRoom for which to extract messages
        user_id: int
            the primary key of the User which must participate in the ChatRoom
        messages_type: str
            determines which type of messages to extract - `read` or `unread`
        count: str
            the count of messages to extract, must be a positive integer
        message_uuid: str
            the primary key of Message from which to extract messages;
            it is needed only for message with the `read` type

        Returns
        -------
        list
            the list of Message models
        """
        # Preprocess and validate input parameters
        count = preprocess_count(count)
        validate_messages_type(messages_type)
        # Call method for the certain messages_type
        method_to_call = getattr(Message.objects, f'{messages_type}_messages')
        messages = method_to_call(chat_uuid=chat_uuid, user_id=user_id)
        # Get read messages before the provided message
        if messages_type == 'read' and message_uuid is not None:
            messages = messages.messages_before_message(message_uuid)
        return list(messages[:count])

    @classmethod
    def send_message(
            cls,
            chat_uuid: str,
            user_id: int,
            text: str):
        """
        Sends the new message to the corresponding chat

        Parameters
        ----------
        chat_uuid: str
            the primary key of the ChatRoom for which to extract messages
        user_id: int
            the primary key of the User which must participate in the ChatRoom
        text: str
            the content of the message
        """
        validate_message_text(text)
        new_message = Message(
            chat_room_id=chat_uuid,
            sender_id=user_id,
            text=text)
        new_message.save()
