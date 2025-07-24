"""Django settings for AdNova."""

import contextlib
import logging
from collections.abc import Callable
from pathlib import Path

import django_stubs_ext
import environ
from django.utils.translation import gettext_lazy as _
from health_check.plugins import plugin_dir

from integrations.yandexai.healthcheck import YandexAIHealthCheck

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

django_stubs_ext.monkeypatch()


# Common settings

DEBUG = env("DJANGO_DEBUG", default=False)

ALLOWED_HOSTS = env(
    "DJANGO_ALLOWED_HOSTS",
    list,
    default=["localhost", "127.0.0.1"],
)


# Integrations

YANDEX_CLOUD_FOLDER_ID = env("YANDEX_CLOUD_FOLDER_ID", default=None)

YANDEX_CLOUD_API_KEY = env("YANDEX_CLOUD_API_KEY", default=None)

YANDEX_CLOUD_INTEGRATION_ENABLED = (
    YANDEX_CLOUD_FOLDER_ID and YANDEX_CLOUD_API_KEY
)


# Register healthchecks

plugin_dir.register(YandexAIHealthCheck)


# Caching

REDIS_URI = env("REDIS_URI", default="redis://localhost:6379")

CACHES = {
    "default": {
        "BACKEND": "django_prometheus.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URI,
        "TIMEOUT": None,
        "KEY_PREFIX": "backend",
        "VERSION": 1,
    },
}


# Celery

CELERY_BROKER_URL = REDIS_URI

CELERY_RESULT_BACKEND = REDIS_URI

CELERY_TIMEZONE = "UTC"

CELERY_WORKER_SEND_TASK_EVENTS = True

CELERY_TASK_SEND_SENT_EVENT = True

CELERY_TASK_TRACK_STARTED = True


# Database

DB_URI = env.db_url("DJANGO_DB_URI", default="sqlite:///db.sqlite3")
DB_URI["ENGINE"] = DB_URI["ENGINE"].replace(
    "django.db.backends", "django_prometheus.db.backends"
)

DATABASES = {"default": {**DB_URI, "CONN_MAX_AGE": 50}}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth."
            "password_validation.UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.NumericPasswordValidator"
        ),
    },
]


# Static files (CSS, JavaScript, Images)

STATIC_ROOT = BASE_DIR / "static"

STATIC_URL = env("DJANGO_STATIC_URL", default="static/")

STATICFILES_DIRS: list[str] = []

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]


# Files

FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440

# Minio

MINIO_STORAGE_ENDPOINT = env("MINIO_ENDPOINT", default=None)

MINIO_STORAGE_ACCESS_KEY = env("MINIO_ACCESS_KEY", default=None)

MINIO_STORAGE_SECRET_KEY = env("MINIO_SECRET_KEY", default=None)

MINIO_STORAGE_USE_HTTPS = env("MINIO_USE_HTTPS", default=False)

MINIO_STORAGE_MEDIA_BUCKET_NAME = env(
    "MINIO_MEDIA_BUCKET_NAME", default="adnova-media"
)

MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = True

MINIO_STORAGE_AUTO_CREATE_MEDIA_POLICY = "GET_ONLY"

MINIO_DEFAULT_CUSTOM_ENDPOINT_URL = (
    "https://"
    if MINIO_STORAGE_USE_HTTPS
    else "http://" + str(MINIO_STORAGE_ENDPOINT)
)

MINIO_STORAGE_MEDIA_URL = (
    env("MINIO_CUSTOM_ENDPOINT_URL", default=MINIO_DEFAULT_CUSTOM_ENDPOINT_URL)
    + "/"
    f"{MINIO_STORAGE_MEDIA_BUCKET_NAME}"
)

MINIO_STORAGE_DEFAULT_ACL = "public-read"

STORAGES = {
    "default": {
        "BACKEND": "minio_storage.storage.MinioMediaStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}


# Cors

CORS_ALLOWED_ORIGINS_FROM_ENV = env("DJANGO_CORS_ALLOWED_ORIGINS", list, ["*"])

if CORS_ALLOWED_ORIGINS_FROM_ENV == ["*"]:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = CORS_ALLOWED_ORIGINS_FROM_ENV


# Forms

FORM_RENDERER = "django.forms.renderers.DjangoTemplates"

FORMS_URLFIELD_ASSUME_HTTPS = False


# Internationalization

DATE_FORMAT = "N j, Y"

DATE_INPUT_FORMATS = [
    "%Y-%m-%d",  # '2006-10-25'
    "%m/%d/%Y",  # '10/25/2006'
    "%m/%d/%y",  # '10/25/06'
    "%b %d %Y",  # 'Oct 25 2006'
    "%b %d, %Y",  # 'Oct 25, 2006'
    "%d %b %Y",  # '25 Oct 2006'
    "%d %b, %Y",  # '25 Oct, 2006'
    "%B %d %Y",  # 'October 25 2006'
    "%B %d, %Y",  # 'October 25, 2006'
    "%d %B %Y",  # '25 October 2006'
    "%d %B, %Y",  # '25 October, 2006'
]

DATETIME_FORMAT = "N j, Y, H:i:s"

DATETIME_INPUT_FORMATS = [
    "%Y-%m-%d %H:%M:%S",  # '2006-10-25 14:30:59'
    "%Y-%m-%d %H:%M:%S.%f",  # '2006-10-25 14:30:59.000200'
    "%Y-%m-%d %H:%M",  # '2006-10-25 14:30'
    "%m/%d/%Y %H:%M:%S",  # '10/25/2006 14:30:59'
    "%m/%d/%Y %H:%M:%S.%f",  # '10/25/2006 14:30:59.000200'
    "%m/%d/%Y %H:%M",  # '10/25/2006 14:30'
    "%m/%d/%y %H:%M:%S",  # '10/25/06 14:30:59'
    "%m/%d/%y %H:%M:%S.%f",  # '10/25/06 14:30:59.000200'
    "%m/%d/%y %H:%M",  # '10/25/06 14:30'
]

DECIMAL_SEPARATOR = "."

FIRST_DAY_OF_WEEK = 1

FORMAT_MODULE_PATH = None

LANGUAGE_CODE = env("DJANGO_LANGUAGE_CODE", default="en-us")

LANGUAGES = [("en", _("English")), ("ru", _("Russian"))]

LOCALE_PATHS: list[str] = []

MONTH_DAY_FORMAT = "F j"

NUMBER_GROUPING = 0

SHORT_DATE_FORMAT = "m/d/Y"

SHORT_DATETIME_FORMAT = "m/d/Y H:i:s"

THOUSAND_SEPARATOR = ","

TIME_FORMAT = "H:i:s"

TIME_INPUT_FORMATS = [
    "%H:%M:%S",  # '14:30:59'
    "%H:%M:%S.%f",  # '14:30:59.000200'
    "%H:%M",  # '14:30'
]

TIME_ZONE = "UTC"

USE_I18N = True

USE_THOUSAND_SEPARATOR = True

USE_TZ = True

YEAR_MONTH_FORMAT = "F Y"


# HTTP

DATA_UPLOAD_MAX_MEMORY_SIZE = None

DATA_UPLOAD_MAX_NUMBER_FIELDS = None

DATA_UPLOAD_MAX_NUMBER_FILES = None

DEFAULT_CHARSET = "utf-8"

FORCE_SCRIPT_NAME = None

INTERNAL_IPS = env(
    "DJANGO_INTERNAL_IPS",
    list,
    default=["127.0.0.1"],
)

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django_guid.middleware.guid_middleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

SIGNING_BACKEND = "django.core.signing.TimestampSigner"

USE_X_FORWARDED_HOST = False

USE_X_FORWARDED_PORT = False

WSGI_APPLICATION = "config.wsgi.application"


# Logging

LOGGER_NAME = "adnova"

LOGGER = logging.getLogger(LOGGER_NAME)

LOGGING_FILTERS = {
    "require_debug_true": {
        "()": "django.utils.log.RequireDebugTrue",
    },
    "require_debug_false": {
        "()": "django.utils.log.RequireDebugFalse",
    },
    "correlation_id": {
        "()": "django_guid.log_filters.CorrelationId",
    },
}

LOGGING_FORMATTERS = {
    "json": {
        "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
        "format": (
            "{levelname}{correlation_id}{asctime}"
            "{name}{pathname}{lineno}{message}"
        ),
        "style": "{",
    },
    "text": {
        "()": "colorlog.ColoredFormatter",
        "format": (
            "{log_color}[{levelname}]{reset} "
            "{light_black}{asctime} {name} | {pathname}:{lineno}{reset}\n"
            "{bold_black}{message}{reset}"
        ),
        "log_colors": {
            "DEBUG": "bold_green",
            "INFO": "bold_cyan",
            "WARNING": "bold_yellow",
            "ERROR": "bold_red",
            "CRITICAL": "bold_purple",
        },
        "style": "{",
    },
}

LOGGING_HANDLERS = {
    "console_debug": {
        "class": "logging.StreamHandler",
        "level": "DEBUG",
        "filters": ["require_debug_true"],
        "formatter": "text",
    },
    "console_prod": {
        "class": "logging.StreamHandler",
        "level": "INFO",
        "filters": ["require_debug_false", "correlation_id"],
        "formatter": "json",
    },
}

LOGGING_LOGGERS = {
    "django": {
        "handlers": ["console_debug", "console_prod"],
        "level": "INFO" if DEBUG else "ERROR",
        "propagate": False,
    },
    "django.request": {
        "handlers": ["console_debug", "console_prod"],
        "level": "INFO" if DEBUG else "ERROR",
        "propagate": False,
    },
    "django.server": {
        "handlers": ["console_debug"],
        "level": "INFO",
        "filters": ["require_debug_true"],
        "propagate": False,
    },
    "django.template": {"handlers": []},
    "django.db.backends.schema": {"handlers": []},
    "django.security": {"handlers": [], "propagate": True},
    "django.db.backends": {
        "handlers": ["console_debug"],
        "filters": ["require_debug_true"],
        "level": "DEBUG",
        "propagate": False,
    },
    "health-check": {
        "handlers": ["console_debug", "console_prod"],
        "level": "INFO" if DEBUG else "ERROR",
        "propagate": False,
    },
    LOGGER_NAME: {
        "handlers": ["console_debug", "console_prod"],
        "level": "DEBUG" if DEBUG else "INFO",
        "propagate": False,
    },
    "root": {
        "handlers": ["console_debug", "console_prod"],
        "level": "INFO" if DEBUG else "ERROR",
        "propagate": False,
    },
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": LOGGING_FILTERS,
    "formatters": LOGGING_FORMATTERS,
    "handlers": LOGGING_HANDLERS,
    "loggers": LOGGING_LOGGERS,
}

LOGGING_CONFIG = "logging.config.dictConfig"


# Models

ABSOLUTE_URL_OVERRIDES: dict[str, Callable] = {}

FIXTURE_DIRS: list[str] = []

INSTALLED_APPS = [
    # Build-in apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Healthcheck
    "health_check",
    "health_check.db",
    "health_check.cache",
    "health_check.storage",
    "health_check.contrib.migrations",
    "health_check.contrib.celery",
    "health_check.contrib.celery_ping",
    # Third-party apps
    "corsheaders",
    "django_extensions",
    "django_guid",
    "django_prometheus",
    "ninja",
    "minio_storage",
    # Internal apps
    "apps.core",
    "apps.advertiser",
    "apps.client",
    "apps.mlscore",
    "apps.campaign",
    # API v1 apps
    "api.v1.clients",
]

# GUID

DJANGO_GUID = {
    "GUID_HEADER_NAME": "Correlation-ID",
    "VALIDATE_GUID": True,
    "RETURN_HEADER": True,
    "EXPOSE_HEADER": True,
    "INTEGRATIONS": [],
    "IGNORE_URLS": [],
    "UUID_LENGTH": 32,
}


# Security

LANGUAGE_COOKIE_AGE = 31449600

LANGUAGE_COOKIE_DOMAIN = None

LANGUAGE_COOKIE_HTTPONLY = False

LANGUAGE_COOKIE_NAME = "django_language"

LANGUAGE_COOKIE_PATH = "/"

LANGUAGE_COOKIE_SAMESITE = "Lax"

LANGUAGE_COOKIE_SECURE = False

SECURE_PROXY_SSL_HEADER = None

CSRF_COOKIE_AGE = 31449600

CSRF_COOKIE_DOMAIN = None

CSRF_COOKIE_HTTPONLY = False

CSRF_COOKIE_NAME = "djangocsrftoken"

CSRF_COOKIE_PATH = "/"

CSRF_COOKIE_SAMESITE = "Lax"

CSRF_COOKIE_SECURE = False

CSRF_FAILURE_VIEW = "django.views.csrf.csrf_failure"

CSRF_HEADER_NAME = "HTTP_X_CSRFTOKEN"

CSRF_TRUSTED_ORIGINS = env(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    list,
    default=["http://localhost", "http://127.0.0.1"],
)

CSRF_USE_SESSIONS = False

SECRET_KEY = env("DJANGO_SECRET_KEY", default="very_insecure_key")

SECRET_KEY_FALLBACKS: list[str] = []


# Sessions

SESSION_CACHE_ALIAS = "default"

SESSION_COOKIE_AGE = 1209600

SESSION_COOKIE_DOMAIN = None

SESSION_COOKIE_HTTPONLY = True

SESSION_COOKIE_NAME = "djangosessionid"

SESSION_COOKIE_PATH = "/"

SESSION_COOKIE_SAMESITE = "Lax"

SESSION_COOKIE_SECURE = False

SESSION_ENGINE = "django.contrib.sessions.backends.db"

SESSION_EXPIRE_AT_BROWSER_CLOSE = False

SESSION_FILE_PATH = None

SESSION_SAVE_EVERY_REQUEST = False

SESSION_SERIALIZER = "django.contrib.sessions.serializers.JSONSerializer"


# Templates

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "autoescape": True,
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "debug": DEBUG,
            "string_if_invalid": "",
            "file_charset": "utf-8",
        },
    },
]


# Testing

TEST_NON_SERIALIZED_APPS: list[str] = []

TEST_RUNNER = "django.test.runner.DiscoverRunner"


# URLs

ROOT_URLCONF = "config.urls"


# debug-toolbar

DEBUG_TOOLBAR_ENABLED = False

with contextlib.suppress(Exception):
    import debug_toolbar  # noqa: F401

    DEBUG_TOOLBAR_ENABLED = True

DEBUG_TOOLBAR_CONFIG = {"SHOW_COLLAPSED": True, "UPDATE_ON_FETCH": True}

if DEBUG and DEBUG_TOOLBAR_ENABLED:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")


# Prometheus

PROMETHEUS_LATENCY_BUCKETS = (
    0.005,
    0.01,
    0.025,
    0.05,
    0.075,
    0.1,
    0.25,
    0.5,
    0.75,
    1.0,
    2.5,
    5.0,
    7.5,
    10.0,
    25.0,
    50.0,
    75.0,
    float("inf"),
)
