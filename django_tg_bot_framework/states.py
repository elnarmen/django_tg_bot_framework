from typing import Any, Optional, cast

from pydantic import BaseModel, Field

from tg_api import Update, Message

from .routes import Router


class BaseState(BaseModel):
    """Базовый класс для всех состояний стейт-машины.

    Fill free to inherite custom state class from BaseState with adding new attributes to Pydantic model scheme.
    """

    state_class_locator: str = Field(
        description='Path-like string specifies how to find required State class. '
                    'Will be initialized by router on state instance creation.',
    )
    router: Router = Field(
        description='Will be initialized by router on state instance creation.',
        exclude=True,
        repr=False,
    )

    class Config:
        allow_mutation = False
        validate_all = True
        extra = 'ignore'

    def enter_state(self) -> Optional['BaseState']:
        """Run any custom logic on state enter.

        Can return state object to force state machine switching to another state.
        """
        pass

    def exit_state(self, state_class_transition: bool) -> None:
        """Run any custom logic on state exit.

        State machine switching to another state is not available from this method.
        """
        pass

    def process(self, event: Any) -> Optional['BaseState']:
        """Run any custom logic to process event.

        Can return state object to force state machine switching to another state.
        """
        pass


class InteractiveState(BaseState):
    def react_on_message(self, message: Message) -> BaseState | None:
        pass

    def react_on_inline_keyboard(self, message: Message, pressed_button_payload: str) -> BaseState | None:
        pass

    def process(self, event: Any) -> BaseState | None:
        """Handle common Telegram API Update event cases.

        Can return state object to switch state machine to another state.
        """
        if not isinstance(event, Update):
            return

        update_event = cast(Update, event)

        if update_event.message:
            # In case regular message or reply keyboard
            return self.react_on_message(update_event.message)
        elif update_event.callback_query:
            # In case user pressed inline keyboard button
            message = update_event.callback_query.message
            pressed_button_payload = update_event.callback_query.data
            return self.react_on_inline_keyboard(message, pressed_button_payload)
        else:
            # Other updates we dont work with
            return
