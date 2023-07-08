from unittest.mock import MagicMock
from typing import ClassVar, Any

import pytest

from django_tg_bot_framework.routes import Router
from django_tg_bot_framework.states import BaseState
from django_tg_bot_framework.state_machine import StateMachine
from django_tg_bot_framework.exceptions import TooLongTransitionError


def test_single_state():
    router = Router()
    first_event = {'event_id': 1}
    second_event = {'event_id': 2}

    @router.register('/')
    class RootState(BaseState):
        enter_state: ClassVar = MagicMock(return_value=None)
        process: ClassVar = MagicMock(return_value=None)
        exit_state: ClassVar = MagicMock(return_value=None)

    state_machine = StateMachine(
        current_state=router.locate('/'),
    )
    state_machine.reenter_state()

    state_machine.process(first_event)
    RootState.enter_state.assert_called_once()
    RootState.process.assert_called_once_with(event=first_event)
    RootState.exit_state.assert_not_called()

    state_machine.process(second_event)
    RootState.enter_state.assert_called_once()
    RootState.process.assert_called_with(event=second_event)
    RootState.exit_state.assert_not_called()


def test_states_transition():
    router = Router()
    first_event = {'event_id': 1}

    @router.register('/first/')
    class FirstState(BaseState):
        counter: int = 0
        enter_state: ClassVar = MagicMock(return_value=None)

        def process(self, event: Any) -> BaseState | None:
            return router.locate('/second/', counter=self.counter + 1)

        exit_state: ClassVar = MagicMock(return_value=None)

    @router.register('/second/')
    class SecondState(BaseState):
        counter: int

        def enter_state(self) -> BaseState | None:
            return router.locate('/first/', counter=self.counter + 1)

        process: ClassVar = MagicMock(return_value=None)
        exit_state: ClassVar = MagicMock(return_value=None)

    state_machine = StateMachine(
        current_state=router.locate('/first/'),
    )
    state_machine.reenter_state()

    state_machine.process(first_event)
    assert state_machine.current_state.state_class_locator == '/first/'
    assert state_machine.current_state.counter == 2

    assert FirstState.enter_state.call_count == 2
    FirstState.exit_state.assert_called_once()

    SecondState.process.assert_not_called()
    SecondState.exit_state.assert_called_once()


def test_inifinite_transitions_loop():
    router = Router()
    calls_counters = {
        'enter_state': 0,
    }

    @router.register('/')
    class RootState(BaseState):
        counter: int = 1

        def enter_state(self) -> BaseState | None:
            calls_counters['enter_state'] += 1
            return router.locate('/', counter=self.counter + 1)

    with pytest.raises(TooLongTransitionError):
        state_machine = StateMachine(
            current_state=router.locate('/'),
            max_transition_length=3,
        )
        state_machine.reenter_state()

    assert calls_counters['enter_state'] == 4


def test_cancel_transition_on_enter_state_failure():
    router = Router()

    @router.register('/first/')
    class FirstState(BaseState):
        def process(self, event: Any) -> BaseState | None:
            return router.locate('/second/')

        exit_state: ClassVar = MagicMock(return_value=None)

    @router.register('/second/')
    class SecondState(BaseState):
        def enter_state(self) -> BaseState | None:
            raise RuntimeError('Oops...')

    state_machine = StateMachine(
        current_state=router.locate('/first/'),
    )
    state_machine.reenter_state()

    with pytest.raises(RuntimeError, match='Oops'):
        state_machine.process(None)

    assert state_machine.current_state.state_class_locator == '/first/'


def test_cancel_transition_on_exit_state_failure():
    router = Router()

    @router.register('/first/')
    class FirstState(BaseState):
        def process(self, event: Any) -> BaseState | None:
            return router.locate('/second/')

        exit_state: ClassVar = MagicMock(return_value=None)

    @router.register('/second/')
    class SecondState(BaseState):
        def enter_state(self) -> None:
            return router.locate('/third/')

        def exit_state(self, state_class_transition: bool) -> None:
            raise RuntimeError('Oops...')

    @router.register('/third/')
    class ThirdState(BaseState):
        pass

    state_machine = StateMachine(
        current_state=router.locate('/first/'),
    )
    state_machine.reenter_state()

    with pytest.raises(RuntimeError, match='Oops'):
        state_machine.process(None)

    assert state_machine.current_state.state_class_locator == '/first/'
