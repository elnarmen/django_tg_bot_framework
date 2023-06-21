import re
import string

from django.core.exceptions import ValidationError
from django.db import models

from .routes import STATE_CLASS_LOCATOR_PATTERN

TG_USERNAME_PATTERN = r"^[a-zA-Z0-9_]{5,50}$"
TG_USERNAME_INVALID_CHARS_PATTERN = r"[^a-zA-Z0-9_]"


def validate_tg_username_friendly_to_user(value: str) -> None:
    """Проводит ту же валидацию, что выполяет БД с помощью constraints, но генерирует понятные пользователю ошибки."""
    if len(value) < 5:
        raise ValidationError("Ник в телеграме должен иметь длину больше 5")

    if value.startswith('@'):
        raise ValidationError("Введите ник в телеграме без символа @.")

    found_invalid_chars = re.findall(TG_USERNAME_INVALID_CHARS_PATTERN, value)
    if found_invalid_chars:
        invalid_chars_description = ", ".join({repr(char) for char in found_invalid_chars})
        raise ValidationError(f"Ник в телеграмме содержит запрещённые символы: {invalid_chars_description}")


def validate_state_class_locator_friendly_to_user(value: str) -> None:
    """Проводит ту же валидацию, что выполяет БД с помощью constraints, но генерирует понятные пользователю ошибки."""
    if not value.startswith('/'):
        raise ValidationError('Локатор класса состояния должен начинаться со слэша `/`.')

    if not value.endswith('/'):
        raise ValidationError('Локатор класса состояния должен заканчиваться слэшом `/`.')

    if ' ' in value:
        raise ValidationError(
            'Локатор класса состояния не может содержать пробелов. Используйте символы тире и подчёркивания.',
        )

    if set(value) & set(string.ascii_uppercase):
        raise ValidationError('Локатор класса состояния содержит символы в верхнем регистре.')

    allowed_symbols = f'{string.ascii_lowercase}{string.digits}_-/'
    prohibited_symbols = set(value) - set(allowed_symbols)

    if prohibited_symbols:
        raise ValidationError(f'Локатор класса состояния содержит запрещённые символы: {prohibited_symbols!r}')


class BaseStateMachineDump(models.Model):
    state_class_locator = models.CharField(
        'Класс состояния',
        blank=True,
        help_text='Тип состояния, в котором сейчас находится диалог с пользователем. '
                  'В поле хранится локатор класса состояния, похожий на строку адреса URL. '
                  'Локатор начинается со слэша <code>/</code> и заканчивается слэшом <code>/</code>, '
                  'содержит только латинские символы a-z, цифры, знаки тире, подчёркивания и слэша <code>/</code>. '
                  'Строго нижний регистр букв.',
        validators=[validate_state_class_locator_friendly_to_user],
    )
    state_params = models.JSONField(
        'Параметры состояния',
        null=True,
        blank=True,
        help_text='Дополнительные параметры того состояния, в котором сейчас находится диалог с пользователем.',
    )

    class Meta:
        abstract = True
        verbose_name = "Стейт-машина"
        verbose_name_plural = "Стейт-машины"
        constraints = [
            models.CheckConstraint(
                check=models.Q(
                    state_class_locator__regex=STATE_CLASS_LOCATOR_PATTERN) | models.Q(state_class_locator=''),
                name="correct_state_class_locator_format",
            ),
        ]


class BaseTgUser(models.Model):
    tg_username = models.CharField(
        "Имя юзера в Tg",
        max_length=50,
        blank=True,
        db_index=True,
        validators=[validate_tg_username_friendly_to_user],
        help_text="Имя для поиска человека в Telegram. "
                  "Обычно выглядит так: @username. Вводите без символа @. "
                  "Поле может быть пустым, если у пользователя tg не указан username.",
    )

    tg_user_id = models.CharField(
        "Id юзера в Tg",
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Пример: 123456789. Чтобы узнать ID пользователя, перешлите сообщение пользователя боту "
                  "<a href='https://t.me/userinfobot'>@userinfobot</a>.",
    )

    class Meta:
        abstract = True
        verbose_name = "Пользователь tg-бота"
        verbose_name_plural = "Пользователи tg-бота"
        constraints = [
            models.CheckConstraint(
                check=models.Q(tg_username__regex=TG_USERNAME_PATTERN) | models.Q(tg_username=''),
                name="tg_username_correspond_to_spec",
            ),
        ]

    def __str__(self):
        tg_username_label = self.tg_username or '???'
        return f'{tg_username_label} ({self.tg_user_id})'
