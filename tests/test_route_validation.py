import pytest

from django_tg_bot_framework.routes import Route
from django_tg_bot_framework.states import BaseState


def test_routes_creation():
    Route(
        state_class_locator='/',
        state_class=BaseState,
        title='корневой роут',
    )

    Route(
        state_class_locator='/inner/',
        state_class=BaseState,
        title='вложенный роут',
    )


@pytest.mark.parametrize("locator,reason", [
    ('without-leading-slash', 'Leading slash symbol'),
    ('/without-trailing-slash', 'Trailing slash symbol'),
    ('/with whitespace/', 'Whitespace symbols are found'),
    ('/WithUpperCase/', 'Uppercase symbols are found'),
    ('/without|prohibited|symbols/', 'Prohibited symbols are found'),
    ('//', 'Check out STATE_CLASS_LOCATOR_REGEXP.'),
])
def test_validation_failures(locator: str, reason: str):
    with pytest.raises(ValueError, match=reason):
        Route(
            state_class_locator=locator,
            state_class=BaseState,
        )


def test_state_class_validation():
    class A():
        pass

    with pytest.raises(ValueError, match='BaseState'):
        Route(
            state_class_locator='/',
            state_class=A,
        )
