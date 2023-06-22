from dataclasses import dataclass
import re
import string
from typing import Type, Callable, TYPE_CHECKING


from .exceptions import UnknownStateClassLocatorError

if TYPE_CHECKING:
    from .states import BaseState

STATE_CLASS_LOCATOR_PATTERN = r"^/([a-z0-9_\-]+/)*$"
STATE_CLASS_LOCATOR_REGEXP = re.compile(STATE_CLASS_LOCATOR_PATTERN)

StateDecoratorType = Callable[[Type['BaseState']], Type['BaseState']]


def validate_state_class_locator(value: str) -> None:
    """Проводит ту же валидацию, что выполяет БД с помощью constraints, но генерирует понятные пользователю ошибки."""
    if not value.startswith('/'):
        raise ValueError(
            f'Wrong state class locator string format {value!r}. Leading slash symbol `/` is absent.',
        )

    if not value.endswith('/'):
        raise ValueError(
            f'Wrong state class locator string format {value!r}. Trailing slash symbol `/` is absent.',
        )

    if ' ' in value:
        raise ValueError(
            f'Wrong state class locator string format {value!r}. '
            'Whitespace symbols are found. Use dashes and underscores instead.',
        )

    found_uppercase_symbols = set(value) & set(string.ascii_uppercase)
    if set(value) & set(string.ascii_uppercase):
        raise ValueError(
            f'Wrong state class locator string format {value!r}. '
            f'Uppercase symbols are found: {found_uppercase_symbols!r}.',
        )

    allowed_symbols = f'{string.ascii_lowercase}{string.digits}_-/'
    prohibited_symbols = set(value) - set(allowed_symbols)

    if prohibited_symbols:
        raise ValueError(
            f'Wrong state class locator string format {value!r}. '
            'Prohibited symbols are found: {prohibited_symbols!r}.',
        )

    if not STATE_CLASS_LOCATOR_REGEXP.match(value):
        raise ValueError(
            f'Wrong state class locator string format {value!r}. Check out STATE_CLASS_LOCATOR_REGEXP.',
        )


@dataclass(frozen=True)
class Route:
    state_class_locator: str
    state_class: Type['BaseState']
    title: str = ''

    def __post_init__(self):
        validate_state_class_locator(self.state_class_locator)

        from .states import BaseState

        if not issubclass(self.state_class, BaseState):
            raise ValueError(
                f'Expects State class inherited from BaseState while {self.state_class} was found.',
            )


class Router(dict[str, Route]):
    """Index of registered routes and state classes."""

    decorators: tuple[StateDecoratorType]

    def __init__(self, decorators: list[StateDecoratorType] | None = None):
        self.decorators = tuple(decorators) if decorators else tuple()

    def register(self, state_class_locator: str, *, title: str = ''):
        """Register a State with specified locator."""
        def register_state_class(state_class: Type['BaseState']) -> Type['BaseState']:
            wrapped_state_class = state_class
            for decorator in reversed(self.decorators):
                wrapped_state_class = decorator(wrapped_state_class)

            route = Route(
                state_class_locator=state_class_locator,
                state_class=wrapped_state_class,
                title=title,
            )
            self[state_class_locator] = route

            return wrapped_state_class
        return register_state_class

    def locate(self, state_class_locator, **kwargs) -> 'BaseState':
        """Create new serializable State."""
        route = self.get(state_class_locator, None)

        if not route:
            raise UnknownStateClassLocatorError(f'Unknown state class locator {state_class_locator}')

        return route.state_class.parse_obj(kwargs | {
            'state_class_locator': state_class_locator,
            'router': self,
        })
