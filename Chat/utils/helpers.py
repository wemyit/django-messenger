from django.conf import settings
from django.http import JsonResponse
from django.utils.translation import ugettext as _
from rest_framework import status


from Chat.models.participant import Participant
from Chat.utils.error_messages import CHAT_ACCESS_MESSAGE
from Chat.utils.validators import validate_messages_type, validate_count


def check_access_to_chat(func):
    def decorator(request, chat_uuid):
        access = Participant.objects.filter(
            chat_room=chat_uuid, person=request.user.id).exists()
        if access:
            return func(request, chat_uuid)
        else:
            return return_error(
                _(CHAT_ACCESS_MESSAGE),
                status.HTTP_403_FORBIDDEN)
    return decorator


def return_error(message, status_code):
    return JsonResponse(
        {
            'error': {
                'status': status_code,
                'message': message
            }
        }, status=status_code)


def preprocess_count(count):
    validate_count(count)
    if count is None:
        count = settings.CHAT_CONFIGURATION['max_messages_count']
    return int(count)
