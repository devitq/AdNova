import contextlib

from django.apps import AppConfig
from django.core.cache import cache


class CoreConfig(AppConfig):
    name = "apps.core"
    label = "core"

    def ready(self) -> None:
        with contextlib.suppress(Exception):
            cache.add("current_date", 0, timeout=None)
