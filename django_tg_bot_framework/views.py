import logging
from typing import Callable

from pydantic import ValidationError

from django.db import transaction
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from tg_api import Update


logger = logging.getLogger('django_tg_bot_framework')


@csrf_exempt
@require_http_methods(["POST"])
@transaction.non_atomic_requests
def process_webhook_call(
    request: HttpRequest,
    *,
    webhook_token: str,
    process_update: Callable[[Update], None],
) -> JsonResponse:
    logger.debug('Telegram webhook called')

    request_token = request.META.get('HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN')
    if not request_token or request_token != webhook_token:
        return JsonResponse({'error': 'Invalid secret token.'}, status=403)

    try:
        logger.debug('Receive JSON encoded Update object: %s', request.body)
        update = Update.parse_raw(request.body)
    except ValidationError as exc:
        logger.warning('Invalid update object format: %s', exc.json())
        return JsonResponse({
            'error': 'Invalid update object format.',
            'details': exc.errors(),
        }, status=400)

    try:
        process_update(update)
    except Exception:
        logger.exception('Webhook call finished with error')

    # Should response with status 200 always even if exception occurs to prevent bot be banned by Tg server
    return JsonResponse({'ok': 'POST request processed.'})
