from rest_framework import serializers

from Chat.models.message import Message


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ('id', 'chat_room', 'sender', 'text', 'date')
