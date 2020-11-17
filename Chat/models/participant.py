from django.db import models
from django.contrib.auth.models import User



class Participant(models.Model):
    person = models.ForeignKey(User, on_delete=models.CASCADE)
    chat_room = models.ForeignKey('Chat.ChatRoom', on_delete=models.CASCADE)

    class Meta:
        db_table = 'participant'
        ordering = ('person',)
        unique_together = ('person', 'chat_room')
