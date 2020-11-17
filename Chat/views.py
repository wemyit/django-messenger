from django.core.exceptions import ValidationError
from django.http import JsonResponse
from rest_framework import permissions
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes

from Chat.models.chat_room import ChatRoom
from Chat.models.unread_message import UnreadMessage
from Chat.serializers import MessageSerializer
from Chat.utils.helpers import return_error, check_access_to_chat
from Chat.utils.validators import validate_request_data

GET_REQUEST_QUERY_PARAMS = ['messages_type', 'count', 'message_uuid']


@api_view(['GET'])
@check_access_to_chat
@permission_classes((permissions.IsAuthenticated,))
def fetch_messages(request, chat_uuid):
    user = request.user
    params = request.query_params.dict()
    try:
        params = {p: params[p] for p in GET_REQUEST_QUERY_PARAMS if p in params}
        # Get messages
        chat_messages = ChatRoom.get_messages(
            chat_uuid=chat_uuid,
            user_id=user.id,
            **params)
        # Mark messages as read for the current user
        UnreadMessage.objects.mark_messages_as_read(
            user_id=user.id,
            chat_uuid=chat_uuid,
            messages_uuids=list(map(lambda x: x.id, chat_messages)))
        # Serialize
        serializer = MessageSerializer(chat_messages, many=True)
        return JsonResponse(serializer.data, safe=False)
    except ValidationError as err:
        return return_error(err.message, status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@check_access_to_chat
@permission_classes((permissions.IsAuthenticated,))
def send_message(request, chat_uuid):
    user = request.user
    data = request.data
    try:
        validate_request_data(data)
        ChatRoom.send_message(
            chat_uuid=chat_uuid,
            user_id=user.id,
            text=data['text'])
        UnreadMessage.objects.mark_messages_as_read(
            user_id=user.id,
            chat_uuid=chat_uuid)
        return JsonResponse({'success': True})
    except ValidationError as err:
        return return_error(err.message, status.HTTP_400_BAD_REQUEST)
