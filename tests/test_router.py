import pytest

from ..exceptions import UnknownStateClassLocatorError
from ..routes import Router
from ..states import BaseState


def test_state_class_registration():
    router = Router()

    @router.register('/', title='Корневое состояние бота')
    class RootState(BaseState):
        pass

    assert router['/'].state_class_locator == '/'
    assert router['/'].state_class == RootState
    assert router['/'].title == 'Корневое состояние бота'

    assert router.locate('/')


def test_locate_with_params():
    router = Router()

    @router.register('/menu/', title='Меню')
    class PromptState(BaseState):
        message_id: int

    assert router.locate('/menu/', message_id=10)


def test_unknown_state_class_locator():
    router = Router()
    with pytest.raises(UnknownStateClassLocatorError):
        router.locate('/menu/', message_id=10)
