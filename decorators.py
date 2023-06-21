import re
from typing import Any, Type

from tg_api import Update

from .states import BaseState
from .routes import Router, StateDecoratorType

TG_COMMAND_REGEXP = re.compile(
    r'''^
        (?P<command>
            /[a-zA-Z0-9_]{0,31}
        )
        \b
    ''',
    re.VERBOSE,
)


def select_new_state_if_command(router: Router, text: str):
    match = TG_COMMAND_REGEXP.match(text)
    if not match:
        return

    state_class_locator = match['command'].lower()

    if not state_class_locator.endswith('/'):
        state_class_locator = f'{state_class_locator}/'

    if state_class_locator in router:
        return router.locate(state_class_locator)


def redirect_tg_commands(state_class: Type[BaseState]) -> StateDecoratorType:
    class WrappedStateClass(state_class):
        def process(self, event: Any) -> BaseState | None:
            if isinstance(event, Update):
                text = event.message and event.message.text or ''
                new_state = select_new_state_if_command(self.router, text)
                return new_state or super().process(event=event)
            return super().process(event=event)
    return WrappedStateClass
