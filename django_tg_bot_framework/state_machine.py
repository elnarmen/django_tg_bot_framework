from itertools import count
import logging
from typing import final, Any

from pydantic import BaseModel, Field

from .states import BaseState
from .exceptions import TooLongTransitionError

logger = logging.getLogger('django_tg_bot_framework')


@final
class StateMachine(BaseModel):
    current_state: BaseState
    max_transition_length: int = Field(
        default=20,
        description='Защита от зацикливания. '
                    'Ограничивает максимальное количество непрерывных переходов между состояниями.',
    )

    def reenter_state(self) -> None:
        next_state = self.current_state.enter_state()
        self.switch_to(next_state or self.current_state)

    def process(self, event: Any):
        """Обрабатывает поступившее событие."""
        next_state = self.current_state.process(event=event)
        self.switch_to(next_state or self.current_state)

    def switch_to(self, next_state: BaseState):
        """Переключает стейт-машину в новое состояние и следует далее по авто-переходам до конечного состояния."""
        if not isinstance(next_state, BaseState):
            raise ValueError(f'Expect BaseState subclass as next_state value, got {next_state!r}')

        counter = count(1)

        if self.current_state == next_state:
            return

        prev_state = self.current_state

        for transition_length in counter:
            if transition_length > self.max_transition_length:
                raise TooLongTransitionError(
                    f'Transition length limit of {self.max_transition_length} is exceeded.',
                )

            logger.debug(
                'State %s → %s.',
                prev_state.state_class_locator,
                next_state.state_class_locator,
            )
            logger.debug('    Old: %s', prev_state)
            logger.debug('    New: %s', next_state)

            state_class_transition = type(prev_state) != type(next_state)
            prev_state.exit_state(state_class_transition=state_class_transition)
            next_next_state = next_state.enter_state()

            if not next_next_state:
                break

            prev_state, next_state = next_state, next_next_state

        self.current_state = next_state
