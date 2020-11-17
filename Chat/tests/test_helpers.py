from unittest.mock import Mock, patch

from django.conf import settings
from django.test import TestCase
from rest_framework import status

from Chat.utils.error_messages import CHAT_ACCESS_MESSAGE
from Chat.utils.helpers import preprocess_count, return_error, check_access_to_chat


class HelpersTestCase(TestCase):

    def test_preprocess_count_none(self):
        output_count = preprocess_count(None)
        self.assertEqual(
            output_count,
            int(settings.CHAT_CONFIGURATION['max_messages_count']))

    def test_preprocess_count_positive_int(self):
        output_count = preprocess_count('10')
        self.assertEqual(output_count, 10)

    def test_return_error(self):
        expected_message = '{"error": {"status": 200, "message": "My message"}}'
        output_message = return_error('My message', 200).content.decode("utf-8")
        self.assertEqual(output_message, expected_message)

    @patch('django.db.models.query.QuerySet.exists')
    def test_check_access_to_chat_accessible(self, mock_exists):
        user_id = 3
        chat_uuid = 'd65d0970-1933-11eb-adc1-0242ac120002'
        mock_func = Mock()
        mock_request = Mock()
        mock_request.user.id = user_id
        mock_exists.return_value = True
        check_access_to_chat(mock_func)(mock_request, chat_uuid)
        mock_func.assert_called_once_with(mock_request, chat_uuid)

    @patch('Chat.utils.helpers.return_error')
    def test_check_access_to_chat_inaccessible(self, mock_return_error):
        user_id = 1
        chat_uuid = 'd65d0970-1933-11eb-adc1-0242ac120002'
        mock_func = Mock()
        mock_request = Mock()
        mock_request.user.id = user_id
        check_access_to_chat(mock_func)(mock_request, chat_uuid)
        mock_return_error.assert_called_once_with(
            CHAT_ACCESS_MESSAGE, status.HTTP_403_FORBIDDEN)
