from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import TestCase

from Chat.utils.error_messages import TEXT_PARAM_MESSAGE
from Chat.utils.validators import (
    validate_count, validate_messages_type,
    POSITIVE_INTEGER_MESSAGE, MESSAGES_TYPES_MESSAGE,
    MAX_COUNT_MESSAGE, validate_message_text, EMPTY_TEXT_MESSAGE, validate_request_data)


class ValidatorsTestCase(TestCase):

    def test_validate_count_odd_int(self):
        validate_count('1')

    def test_validate_count_even_int(self):
        validate_count('2')

    def test_validate_count_empty_string(self):
        with self.assertRaises(ValidationError) as err:
            validate_count('')
        self.assertEqual(
            err.exception.message,
            POSITIVE_INTEGER_MESSAGE)

    def test_validate_count_none(self):
        validate_count(None)

    def test_validate_count_float(self):
        with self.assertRaises(ValidationError) as err:
            validate_count('1.1')
        self.assertEqual(
            err.exception.message,
            POSITIVE_INTEGER_MESSAGE)

    def test_validate_count_greater_than_max(self):
        count = settings.CHAT_CONFIGURATION['max_messages_count'] + '0'
        max_count = settings.CHAT_CONFIGURATION['max_messages_count']
        with self.assertRaises(ValidationError) as err:
            validate_count(count)
        self.assertEqual(
            err.exception.message,
            MAX_COUNT_MESSAGE.format(max_count))

    def test_validate_count_zero(self):
        with self.assertRaises(ValidationError) as err:
            validate_count('0')
        self.assertEqual(
            err.exception.message,
            POSITIVE_INTEGER_MESSAGE)

    def test_validate_count_negative(self):
        with self.assertRaises(ValidationError) as err:
            validate_count('-1')
        self.assertEqual(
            err.exception.message,
            POSITIVE_INTEGER_MESSAGE)

    def test_validate_message_type_read_lower(self):
        validate_messages_type('read')

    def test_validate_message_type_unread_lower(self):
        validate_messages_type('unread')

    def test_validate_message_type_read_upper(self):
        with self.assertRaises(ValidationError) as err:
            validate_messages_type('READ')
        self.assertEqual(
            err.exception.message,
            MESSAGES_TYPES_MESSAGE)

    def test_validate_message_type_unread_upper(self):
        with self.assertRaises(ValidationError) as err:
            validate_messages_type('UNREAD')
        self.assertEqual(
            err.exception.message,
            MESSAGES_TYPES_MESSAGE)

    def test_validate_message_type_empty(self):
        with self.assertRaises(ValidationError) as err:
            validate_messages_type('')
        self.assertEqual(
            err.exception.message,
            MESSAGES_TYPES_MESSAGE)

    def test_validate_message_type_none(self):
        with self.assertRaises(ValidationError) as err:
            validate_messages_type(None)
        self.assertEqual(
            err.exception.message,
            MESSAGES_TYPES_MESSAGE)

    def test_validate_message_type_custom_string(self):
        with self.assertRaises(ValidationError) as err:
            validate_messages_type('Custom string')
        self.assertEqual(
            err.exception.message,
            MESSAGES_TYPES_MESSAGE)

    def test_validate_message_text_none(self):
        with self.assertRaises(ValidationError) as err:
            validate_message_text(None)
        self.assertEqual(
            err.exception.message,
            EMPTY_TEXT_MESSAGE)

    def test_validate_message_text_empty_string(self):
        with self.assertRaises(ValidationError) as err:
            validate_message_text('')
        self.assertEqual(
            err.exception.message,
            EMPTY_TEXT_MESSAGE)

    def test_validate_message_text_valid_string(self):
        validate_message_text('Hello, how are you?')

    def test_validate_request_data_none(self):
        with self.assertRaises(ValidationError) as err:
            validate_request_data(None)
        self.assertEqual(
            err.exception.message,
            TEXT_PARAM_MESSAGE)

    def test_validate_request_data_empty(self):
        with self.assertRaises(ValidationError) as err:
            validate_request_data({})
        self.assertEqual(
            err.exception.message,
            TEXT_PARAM_MESSAGE)

    def test_validate_request_data_extra_params(self):
        with self.assertRaises(ValidationError) as err:
            validate_request_data({'test_param': 'test_content'})
        self.assertEqual(
            err.exception.message,
            TEXT_PARAM_MESSAGE)

    def test_validate_request_data_with_text(self):
        validate_request_data({'text': 'test_content'})
