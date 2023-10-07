Models
======
.. module:: django_tg_bot_framework.models

Models for working with Telegram user profiles and state machines.

.. autoclass:: django_tg_bot_framework.models.BaseStateMachineDump
    :members:
    :undoc-members:
    :exclude-members: state_class_locator, state_params

.. autoclass:: django_tg_bot_framework.models.TgUserProfileMixin
    :members:
    :undoc-members:
    :exclude-members: tg_username, tg_user_id

.. autofunction:: django_tg_bot_framework.models.validate_state_class_locator_friendly_to_user
.. autofunction:: django_tg_bot_framework.models.validate_tg_username_friendly_to_user
