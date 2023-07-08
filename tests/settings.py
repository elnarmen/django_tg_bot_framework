DEBUG = True
USE_TZ = True

SECRET_KEY = "secret-key-mock"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

INSTALLED_APPS = []

MIDDLEWARE_CLASSES = []
