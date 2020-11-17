import uuid
from collections import Iterable

from django.db import models


class UnreadMessageManager(models.Manager):
    def mark_messages_as_read(self, user_id: int, chat_uuid: str, messages_uuids=None):
        lookups = dict(participant__person=user_id,
                       participant__chat_room=chat_uuid)
        if type(messages_uuids) in [str, uuid.UUID]:
            lookups['message'] = messages_uuids
        elif isinstance(messages_uuids, Iterable):
            lookups['message__in'] = messages_uuids
        self.get_queryset().filter(**lookups).delete()


class UnreadMessage(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    message = models.ForeignKey('Chat.Message', on_delete=models.CASCADE)
    participant = models.ForeignKey('Chat.Participant', on_delete=models.CASCADE)
    objects = UnreadMessageManager()
