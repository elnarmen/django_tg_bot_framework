# Django Telegram Bot Framework

Фреймворк для создания чат-ботов Telegram на базе Django. Предоставляет свою стейт-машину, вебхук и редактируемые текстовки в БД.


## Как развернуть local-окружение

Для запуска ПО вам понадобятся консольный Git, Docker и Docker Compose. Инструкции по их установке ищите на официальных сайтах:

- [Install Docker Desktop](https://www.docker.com/get-started/)
- [Install Docker Compose](https://docs.docker.com/compose/install/)

Склонируйте репозиторий.

В репозитории используются хуки pre-commit, чтобы автоматически запускать линтеры и автотесты. Перед началом разработки установите [pre-commit package manager](https://pre-commit.com/).

В корне репозитория запустите команду для настройки хуков:

```shell
$ pre-commit install
```

В последующем при коммите автоматически будут запускаться линтеры и автотесты. Есть линтеры будет недовольны, или автотесты сломаются, то коммит прервётся с ошибкой.

Сначала скачайте и соберите докер-образы с помощью Docker Сompose:

```shell
$ docker compose pull --ignore-buildable
$ docker compose build
```


<a name="development"></a>
## Как вести разработку

<a name="update-local-env"></a>
### Как обновить local-окружение

Чтобы обновить local-окружение до последней версии подтяните код из центрального окружения и пересоберите докер-образы:

``` shell
$ git pull
$ docker compose build
```

<a name="add-python-package-to-django-image"></a>
### Как установить python-пакет в образ

В качестве менеджера пакетов для образа используется [Poetry](https://python-poetry.org/docs/).

Конфигурационные файлы Poetry `pyproject.toml` и `poetry.lock` проброшены в контейнер в виде volume, поэтому изменения зависимостей внутри контейнера попадают и наружу в git-репозиторий.

Вот пример как добавить в зависимости библиотеку asks. Запустите все контейнеры. Подключитесь к уже работающему контейнеру `django_tg_bot_framework` и внутри запустите команду `poetry add asks`:

```shell
$ docker compose up -d
$ docker compose exec django_tg_bot_framework bash
container:$ poetry add asks
```

Конфигурационные файлы `pyproject.toml` и `poetry.lock` обновятся не только внутри контейнера, но и в репозитории благодаря настроенным docker volumes. Осталось только закоммитить изменения.

Чтобы все новые контейнеры также получали свежий набор зависимостей не забудьте обновить докер-образ:

```shell
$ docker compose build django_tg_bot_framework
```

Аналогичным образом можно удалять python-пакеты.

<a name="run-python-linters"></a>
### Как запустить линтеры Python

Линтеры запускаются в отдельном docker-контейнере, а код подключается к нему с помощью volume. Например, чтобы проверить линтером код в каталогах `django_tg_bot_framework` и `tests` запустите команду:

```shell
$ docker compose run --rm py-linters flake8 /django_tg_bot_framework/ /tests/
[+] Building 0.0s (0/0)
[+] Building 0.0s (0/0)
/django_tg_bot_framework/models.py:118:1: W391 blank line at end of file
1
```
Цифра в конце `1` -- это количество найденных линтером ошибок форматирования кода.

Тот же образ с линтером можно использовать, чтобы подсветить ошибки форматирования прямо внутри IDE. Вот пример настройки Sublime Text с предустановленными плагинами [SublimeLinter](http://www.sublimelinter.com/en/stable/) и [SublimeLinter-flake8](https://packagecontrol.io/packages/SublimeLinter-flake8):

```jsonc
// project settings file
{
    "settings": {
        // specify folder where docker-compose.yaml file placed to be able to launch `docker compose`
        "SublimeLinter.linters.flake8.working_dir": "/path/to/repo/",
        "SublimeLinter.linters.flake8.executable": ["docker", "compose", "run", "--rm", "py-linters", "flake8"],
    },
}
```

<a name="run-tests"></a>
### Как запустить тесты

В проекте используются автотесты [pytest](https://docs.pytest.org/). Запустить их можно так:

```shell
$ docker compose run --rm django_tg_bot_framework pytest
=========================== test session starts ===========================
platform linux -- Python 3.11.4, pytest-7.3.2, pluggy-1.2.0
rootdir: /opt/app/src
plugins: django-4.5.2, httpx-0.22.0, anyio-3.7.0
collected 23 items

test_decorators.py ......                                                                                                                                                        [ 26%]
test_route_validation.py ........                                                                                                                                                [ 60%]
test_router.py ...                                                                                                                                                               [ 73%]
test_state_machine.py .....                                                                                                                                                      [ 95%]
test_states.py .                                                                                                   [100%]

============================================================= 6 passed in 0.22s==============================================
```

Если вы чините поломанный тест, часто его запускаете и не хотите ждать когда отработают остальные, то можно запускать их по-отдельности. При этом полезно включать опцию `-s`, чтобы pytest не перехватывал вывод в консоль и выводил все сообщения. Пример для теста `test_redirect_tg_commands` из файла `tests/test_decorators.py.py`:

```shell
$ docker compose run --rm django_tg_bot_framework pytest -s tests/test_decorators.py::test_redirect_tg_commands

```

Подробнее про [Pytest usage](https://docs.pytest.org/en/6.2.x/usage.html).

