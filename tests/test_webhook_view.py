from contextvars import ContextVar
from typing import Callable
from unittest.mock import MagicMock

from pytest_httpx import HTTPXMock

from django.test import Client, override_settings
from django.urls import reverse, path

from tg_api import Update

from django_tg_bot_framework.views import process_webhook_call
from django_tg_bot_framework.contextvars_tools import set_contextvar


process_update_callable: ContextVar[Callable[[...], ...]] = ContextVar('process_update_callable')

urlpatterns = [
    path(
        '/webhook/',
        process_webhook_call,
        name='webhook',
        kwargs={
            'process_update': lambda *args, **kwargs: process_update_callable.get()(*args, **kwargs),
            'webhook_token': 'secret-webhook-token',
        },
    ),
]


@override_settings(ROOT_URLCONF=__name__)
def test_success(
    httpx_mock: HTTPXMock,
):
    process_update = MagicMock(return_value=None)

    request_payload = {
        'update_id': 1,
        'message': {
            'message_id': 101,
            'from': {
                'id': 4114,
                'is_bot': False,
                'first_name': 'Иван Петров',
                'username': 'ivan_petrov',
            },
            'date': 0,
            'chat': {
                'id': 90001,  # noqa A003
                'type': 'private',  # noqa A003
            },
        },
    }
    expected_update = Update.parse_obj(request_payload)

    with set_contextvar(process_update_callable, process_update):

        client = Client(headers={
            'X-Telegram-Bot-Api-Secret-Token': 'secret-webhook-token',
        })

        response = client.post(
            reverse('webhook'),
            request_payload,
            content_type='application/json',
        )
        assert response.status_code == 200
        process_update.assert_called_once_with(expected_update)

    # TODO проверить, что отсутствует вызов logger.exception или logger.warning


@override_settings(ROOT_URLCONF=__name__)
def test_reject_unauthorized():
    client = Client()
    response = client.post(
        reverse('webhook'),
        {'update_id': 1},
        content_type='application/json',
    )
    assert response.status_code == 403
    assert response.json()['error'] == 'Invalid secret token.'


@override_settings(ROOT_URLCONF=__name__)
def test_reject_invalid_update():
    client = Client(headers={
        'X-Telegram-Bot-Api-Secret-Token': 'secret-webhook-token',
    })

    response = client.post(
        reverse('webhook'),
        {},
        content_type='application/json',
    )
    assert response.status_code == 400
    assert response.json()['error'] == 'Invalid update object format.'
    assert response.json()['details'] == [
        {
            'loc': ['update_id'],
            'msg': 'field required',
            'type': 'value_error.missing',
        },
    ]

# TODO test_ignore_non_json_request():

# TODO test_logs_invalid_update_object_format():

# TODO def test_webhook_response_200_on_handler_failure():

# TODO def test_handler_timeout_limitation():
