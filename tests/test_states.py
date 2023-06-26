from django_tg_bot_framework.states import BaseState
from django_tg_bot_framework.routes import Router


def test_state_ignore_unknown_args():
    router = Router()
    router.register('/')(BaseState)

    found_state = router.locate('/', extra_argument=1)
    assert not hasattr(found_state, 'extra_argument')
