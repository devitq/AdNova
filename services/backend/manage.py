#!/usr/bin/env python
# ruff: noqa: PLC0415
"""Django's command-line utility for administrative tasks."""

import os
import sys


def main() -> None:
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        e = """Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"""
        raise ImportError(e) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
