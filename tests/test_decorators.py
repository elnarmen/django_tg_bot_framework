import pytest

from tg_api import Update

from django_tg_bot_framework.decorators import redirect_tg_commands
from django_tg_bot_framework.routes import Router
from django_tg_bot_framework.states import BaseState
from django_tg_bot_framework.state_machine import StateMachine


@pytest.mark.parametrize(
    "text,locator",
    [
        (None, '/'),
        ('some text', '/'),
        ('/starting', '/'),
        ('/start', '/start/'),
        ('/stArt', '/start/'),
        ('/start with extra text', '/start/'),
    ],
)
def test_redirect_tg_commands(text: str | None, locator: str):
    router = Router(decorators=[redirect_tg_commands])

    @router.register('/', title='Корневое состояние бота')
    class RootState(BaseState):
        pass

    @router.register('/start/')
    class StartState(BaseState):
        pass

    update = Update(
        update_id=1,
        message={
            'message_id': 1,
            'date': 1,
            'chat': {
                'id': 43,
                'type': 'private',
            },
        },
    )
    if text is not None:
        update.message.text = text

    state_machine = StateMachine(current_state=router.locate('/'))
    state_machine.reenter_state()
    state_machine.process(update)

    assert state_machine.current_state.state_class_locator == locator
