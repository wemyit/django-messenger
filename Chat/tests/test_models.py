from django.db.models import Max, Min
from django.test import TestCase

from Chat.models.chat_room import ChatRoom
from Chat.models.message import Message
from Chat.models.participant import Participant
from Chat.models.unread_message import UnreadMessage
from django.contrib.auth.models import User


class UnreadMessageTestCase(TestCase):
    fixtures = ['fixtures.json']

    def setUp(self):
        self.user = User.objects.get(id=3)
        self.chat_uuid = 'd65d0970-1933-11eb-adc1-0242ac120002'
        self.participant = Participant.objects.get(
            person=self.user, chat_room=self.chat_uuid)
        self.user_unreadmessages = UnreadMessage.objects.filter(participant=self.participant)

    def test_mark_messages_as_read_empty_uuids(self):
        # Emtpy list
        test_messages_uuids = []
        # Expect 10 unread messages for the current participant
        expected_unreadmessages = list(self.user_unreadmessages.values_list('id', flat=True))
        # Pass empty list
        UnreadMessage.objects.mark_messages_as_read(
            user_id=self.user.id,
            chat_uuid=self.chat_uuid,
            messages_uuids=test_messages_uuids)
        # Output 10 unread messages for the current participant
        output_unreadmessages = list(self.user_unreadmessages.values_list('id', flat=True))
        # Assert that nothing changed
        self.assertEqual(output_unreadmessages, expected_unreadmessages)

    def test_mark_messages_as_read_uuids_none(self):
        # Expect empty list
        expected_unreadmessages = []
        # Do not provide the list of messages to delete
        UnreadMessage.objects.mark_messages_as_read(
            user_id=self.user.id,
            chat_uuid=self.chat_uuid)
        # Output unread messages for the current participant
        output_unreadmessages = list(self.user_unreadmessages.values_list('id', flat=True))
        # Assert that 10 unread messages marked as read
        self.assertEqual(output_unreadmessages, expected_unreadmessages)

    def test_mark_messages_as_read_uuids_not_exist(self):
        # List of unread messages which do not belong to the current participant
        test_messages_uuids = list(
            Message.objects.exclude(
                unreadmessage__participant=self.participant
            ).values_list('id', flat=True))
        # Expect 10 unread messages for the current participant
        expected_unreadmessages = list(self.user_unreadmessages.values_list('id', flat=True))
        # Pass unread messages list
        UnreadMessage.objects.mark_messages_as_read(
            user_id=self.user.id,
            chat_uuid=self.chat_uuid,
            messages_uuids=test_messages_uuids)
        # Output 10 unread messages for the current participant
        output_unreadmessages = list(self.user_unreadmessages.values_list('id', flat=True))
        # Assert that nothing changed
        self.assertEqual(output_unreadmessages, expected_unreadmessages)

    def test_mark_messages_as_read_one_message(self):
        # Last message
        test_messages_uuids = self.user_unreadmessages.last().message.id
        # Expect 9 unread messages for the current participant
        expected_unreadmessages = list(
            self.user_unreadmessages
            .exclude(message=test_messages_uuids)
            .values_list('id', flat=True))
        # Pass one message
        UnreadMessage.objects.mark_messages_as_read(
            user_id=self.user.id,
            chat_uuid=self.chat_uuid,
            messages_uuids=test_messages_uuids)
        # Output 9 unread messages for the current participant
        output_unreadmessages = list(self.user_unreadmessages.values_list('id', flat=True))
        self.assertEqual(output_unreadmessages, expected_unreadmessages)

    def test_mark_messages_as_read_multiple_uuids(self):
        # List of 5 unread messages for the current participant
        test_messages_uuids = list(self.user_unreadmessages[:5].values_list('message_id'))
        # Expect list of remaining 5 unread messages for the current participant
        expected_unreadmessages = list(
            self.user_unreadmessages
            .exclude(message__in=test_messages_uuids)
            .values_list('id', flat=True))
        # Pass list of 5 unread messages
        UnreadMessage.objects.mark_messages_as_read(
            user_id=self.user.id,
            chat_uuid=self.chat_uuid,
            messages_uuids=test_messages_uuids)
        # Output list of remaining 5 unread messages for the current participant
        output_unreadmessages = list(self.user_unreadmessages.values_list('id', flat=True))
        self.assertEqual(output_unreadmessages, expected_unreadmessages)


class MessageTestCase(TestCase):
    fixtures = ['fixtures.json']

    def test_get_message_date(self):
        # Take first message
        message = Message.objects.first()
        # Get its date
        output_message_date = Message.objects.get_message_date(message.id)
        # Assert that it returns the same date
        self.assertEqual(message.date, output_message_date[0])

    def test_messages_before_message_first_message(self):
        # Take first message
        message = Message.objects.first()
        expected_messages = Message.objects.all()[1:]
        output_messages = Message.objects.all().messages_before_message(message.id)
        # Assert that it returns all messages except first
        self.assertEqual(
            list(output_messages.values_list('id', flat=True)),
            list(expected_messages.values_list('id', flat=True)))

    def test_messages_before_message_last_message(self):
        # Take first message
        message = Message.objects.last()
        expected_messages = []
        output_messages = Message.objects.all().messages_before_message(message.id)
        # Assert that it return an empty list
        self.assertEqual(
            list(output_messages.values_list('id', flat=True)),
            expected_messages)

    def test_read_messages_empty_chat(self):
        # Chat without messages
        chat_uuid = '36323c8f-47d1-4023-85d3-ad047d0275f8'
        # User which participates
        user_id = 3
        expected_messages = []
        output_messages = Message.objects.read_messages(chat_uuid, user_id)
        # Assert that list is empty
        self.assertEqual(list(output_messages), expected_messages)

    def test_read_messages_all_unread(self):
        # Chat with 10 messages
        chat_uuid = 'd65d0970-1933-11eb-adc1-0242ac120002'
        # User which participates
        user_id = 3
        expected_messages = []
        output_messages = Message.objects.read_messages(chat_uuid, user_id)
        # Assert that user didn't read any message
        self.assertEqual(list(output_messages), expected_messages)

    def test_read_messages_all_read(self):
        # Chat with 10 messages
        chat_uuid = 'd65d0970-1933-11eb-adc1-0242ac120002'
        # User which participates
        user_id = 5
        expected_messages = Message.objects.filter(chat_room=chat_uuid)
        output_messages = Message.objects.read_messages(chat_uuid, user_id)
        # Assert that user read all messages
        self.assertEqual(
            list(output_messages.values_list('id', flat=True)),
            list(expected_messages.values_list('id', flat=True)))
        # Assert that first message is the earliest
        self.assertEqual(
            output_messages.first().date,
            expected_messages.aggregate(Max('date'))['date__max'])
        # Assert that last message is the latest
        self.assertEqual(
            output_messages.last().date,
            expected_messages.aggregate(Min('date'))['date__min'])

    def test_unread_messages_empty_chat(self):
        # Chat without messages
        chat_uuid = '36323c8f-47d1-4023-85d3-ad047d0275f8'
        # User which participates
        user_id = 3
        expected_messages = []
        output_messages = Message.objects.unread_messages(chat_uuid, user_id)
        # Assert that list is empty
        self.assertEqual(list(output_messages), expected_messages)

    def test_unread_messages_all_unread(self):
        # Chat with 10 messages
        chat_uuid = 'd65d0970-1933-11eb-adc1-0242ac120002'
        # User which participates
        user_id = 3
        expected_messages = Message.objects.filter(chat_room=chat_uuid).reverse()
        output_messages = Message.objects.unread_messages(chat_uuid, user_id)
        # Assert that user didn't read any message
        self.assertEqual(
            list(output_messages.values_list('id', flat=True)),
            list(expected_messages.values_list('id', flat=True)))
        # Assert that last message is the earliest
        self.assertEqual(
            output_messages.last().date,
            expected_messages.aggregate(Max('date'))['date__max'])
        # Assert that first message is the latest
        self.assertEqual(
            output_messages.first().date,
            expected_messages.aggregate(Min('date'))['date__min'])

    def test_unread_messages_all_read(self):
        # Chat with 10 messages
        chat_uuid = 'd65d0970-1933-11eb-adc1-0242ac120002'
        # User which participates
        user_id = 5
        expected_messages = []
        output_messages = Message.objects.unread_messages(chat_uuid, user_id)
        # Assert that user read all messages
        self.assertEqual(list(output_messages), expected_messages)


class ChatRoomTestCase(TestCase):
    fixtures = ['fixtures.json']

    def setUp(self):
        # Chat with 10 messages
        self.chat_uuid = 'd65d0970-1933-11eb-adc1-0242ac120002'

    def test_get_messages_five_last_read_messages(self):
        # User which read all 10 messages
        user_id = 5
        expected_messages = list(Message.objects.filter(chat_room=self.chat_uuid)[:5])
        output_messages = ChatRoom.get_messages(
            chat_uuid=self.chat_uuid,
            user_id=user_id,
            messages_type='read',
            count='5')
        # Assert that it returns 5 most recent read messages
        self.compare_messages(expected_messages, output_messages)

    def test_get_messages_first_five_read_messages(self):
        # User which read all 10 messages
        user_id = 5
        messages = Message.objects.filter(chat_room=self.chat_uuid)
        expected_messages = list(messages[5:])
        output_messages = ChatRoom.get_messages(
            chat_uuid=self.chat_uuid,
            user_id=user_id,
            messages_type='read',
            count='5',
            message_uuid=messages[4].id)
        # Assert that it returns first 5 read messages
        self.compare_messages(expected_messages, output_messages)

    def test_get_messages_after_last_read_message(self):
        # User which read all 10 messages
        user_id = 5
        messages = Message.objects.filter(chat_room=self.chat_uuid)
        expected_messages = []
        output_messages = ChatRoom.get_messages(
            chat_uuid=self.chat_uuid,
            user_id=user_id,
            messages_type='read',
            count='5',
            message_uuid=messages.last().id)
        # Assert that it returns an empty list
        self.assertEqual(list(output_messages), expected_messages)

    def test_get_messages_five_last_unread_messages(self):
        # User which has 10 unread messages
        user_id = 3
        messages_to_delete = UnreadMessage.objects.filter(
            participant__person=user_id,
            participant__chat_room=self.chat_uuid)[:5]
        UnreadMessage.objects.filter(id__in=messages_to_delete).delete()
        expected_messages = list(Message.objects.filter(chat_room=self.chat_uuid).reverse()[5:])
        output_messages = ChatRoom.get_messages(
            chat_uuid=self.chat_uuid,
            user_id=user_id,
            messages_type='unread',
            count='5')
        # Assert that it returns 5 most recent unread messages
        self.compare_messages(expected_messages, output_messages)

    def test_get_messages_first_five_unread_messages(self):
        # User which has 10 unread messages
        user_id = 3
        expected_messages = list(Message.objects.filter(chat_room=self.chat_uuid).reverse()[:5])
        output_messages = ChatRoom.get_messages(
            chat_uuid=self.chat_uuid,
            user_id=user_id,
            messages_type='unread',
            count='5')
        # Assert that it returns first 5 unread messages
        self.compare_messages(expected_messages, output_messages)

    def test_send_message(self):
        # User which participates
        user_id = 3
        text = 'Test send message'
        ChatRoom.send_message(
            chat_uuid=self.chat_uuid,
            user_id=user_id,
            text=text)
        # Get last message
        new_message = Message.objects.latest('date')
        # Assert that latest message is what we sent
        self.assertEqual(new_message.text, text)
        # Extract chat participants except message sender
        expected_participants = Participant.objects.filter(
            chat_room=self.chat_uuid).exclude(
            person=user_id).values_list('id', flat=True)
        # Participants which have new message as unread
        output_participants = UnreadMessage.objects.filter(
            message=new_message).values_list('participant_id', flat=True)
        # Assert that chat participants except message sender get new message as unread
        self.assertEqual(list(output_participants), list(expected_participants))

    def compare_messages(self, expected_messages, output_messages):
        self.assertEqual(
            list(map(lambda x: x.id, output_messages)),
            list(map(lambda x: x.id, expected_messages)))
