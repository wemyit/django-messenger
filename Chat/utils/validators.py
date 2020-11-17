import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from Chat.utils.error_messages import POSITIVE_INTEGER_MESSAGE, MAX_COUNT_MESSAGE, MESSAGES_TYPES_MESSAGE, \
    EMPTY_TEXT_MESSAGE, TEXT_PARAM_MESSAGE

VALID_COUNT_REGEX = r'^[1-9]\d*$'
VALID_MESSAGES_TYPES = ['read', 'unread']


def validate_count(count):
    if count is not None:
        if not re.search(VALID_COUNT_REGEX, count):
            raise ValidationError(_(POSITIVE_INTEGER_MESSAGE))
        max_count = settings.CHAT_CONFIGURATION['max_messages_count']
        if int(count) > int(max_count):
            raise ValidationError(_(MAX_COUNT_MESSAGE.format(max_count)))


def validate_messages_type(messages_type):
    if messages_type not in VALID_MESSAGES_TYPES:
        raise ValidationError(_(MESSAGES_TYPES_MESSAGE))


def validate_message_text(text):
    if not text:
        raise ValidationError(_(EMPTY_TEXT_MESSAGE))


def validate_request_data(data):
    if data is None or 'text' not in data.keys():
        raise ValidationError(_(TEXT_PARAM_MESSAGE))
