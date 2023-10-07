process_webhook_call
====================

A view for securely handling incoming webhook requests from the Telegram API.

.. autofunction:: django_tg_bot_framework.views.process_webhook_call

- Checks the security token in the request to see if it matches the expected token.
- Parses the incoming request to get the ``Update`` object from Telegram API.
- Passes the ``Update`` object to the ``process_update`` function for further processing.
- Always returns a response with status 200, even if an error occurs, to avoid the Telegram server blocking the bot.
