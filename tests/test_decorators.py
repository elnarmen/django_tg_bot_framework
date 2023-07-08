from typing import Any, Type

from django_tg_bot_framework.routes import Router, StateDecoratorType
from django_tg_bot_framework.states import BaseState
from django_tg_bot_framework.state_machine import StateMachine


def test_simple_logging_decorator():
    process_calls_log = []

    def log_process_calls(state_class: Type[BaseState]) -> StateDecoratorType:
        class WrappedStateClass(state_class):
            def process(self, event: Any) -> BaseState | None:
                process_calls_log.append(event)
                return super().process(event=event)
        return WrappedStateClass

    router = Router(decorators=[log_process_calls])

    @router.register('/', title='Корневое состояние бота')
    class RootState(BaseState):
        pass

    @router.register('/start/')
    class StartState(BaseState):
        pass

    state_machine = StateMachine(current_state=router.locate('/'))
    state_machine.reenter_state()
    state_machine.process('first_event')
    state_machine.switch_to(router.locate('/start/'))
    state_machine.process('second_event')

    assert process_calls_log == [
        'first_event',
        'second_event',
    ]
