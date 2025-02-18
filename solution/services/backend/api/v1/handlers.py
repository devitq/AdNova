import logging
from collections.abc import Callable
from http import HTTPStatus as status
from typing import Any

import django.core.exceptions
import django.http
import ninja.errors
from django.http import HttpRequest, HttpResponse
from ninja import NinjaAPI

from config.errors import ConflictError, ForbiddenError

logger = logging.getLogger("django")


def handle_validation_error(
    request: HttpRequest,
    exc: ninja.errors.ValidationError,
    router: NinjaAPI,
) -> HttpResponse:
    return router.create_response(
        request,
        {"detail": exc.errors},
        status=status.BAD_REQUEST,
    )


def handle_django_validation_error(
    request: HttpRequest,
    exc: django.core.exceptions.ValidationError,
    router: NinjaAPI,
) -> HttpResponse:
    detail = list(exc)

    if hasattr(exc, "error_dict"):
        detail = dict(exc)

    return router.create_response(
        request,
        {"detail": detail},
        status=status.BAD_REQUEST,
    )


def handle_authentication_error(
    request: HttpRequest,
    exc: ninja.errors.AuthenticationError,
    router: NinjaAPI,
) -> HttpResponse:
    return router.create_response(
        request,
        {"detail": status.UNAUTHORIZED.phrase},
        status=status.UNAUTHORIZED,
    )


def handle_forbidden_error(
    request: HttpRequest,
    exc: ForbiddenError,
    router: NinjaAPI,
) -> HttpResponse:
    return router.create_response(
        request,
        {"detail": exc.message},
        status=status.FORBIDDEN,
    )


def handle_not_found_error(
    request: HttpRequest,
    exc: Exception,
    router: NinjaAPI,
) -> HttpResponse:
    return router.create_response(
        request,
        {"detail": status.NOT_FOUND.phrase},
        status=status.NOT_FOUND,
    )


def handle_conflict_error(
    request: HttpRequest,
    exc: ConflictError,
    router: NinjaAPI,
) -> HttpResponse:
    detail = list(exc.validation_error)

    if hasattr(exc, "error_dict"):
        detail = dict(exc.validation_error)

    return router.create_response(
        request,
        {"detail": detail},
        status=status.CONFLICT,
    )


def handle_unknown_exception(
    request: HttpRequest,
    exc: Exception,
    router: NinjaAPI,
) -> HttpResponse:
    logger.exception(exc)

    return router.create_response(
        request,
        {"detail": status.INTERNAL_SERVER_ERROR.phrase},
        status=status.INTERNAL_SERVER_ERROR,
    )


exception_handlers: list[tuple[Any, Callable]] = [
    (ninja.errors.ValidationError, handle_validation_error),
    (django.core.exceptions.ValidationError, handle_django_validation_error),
    (ninja.errors.AuthenticationError, handle_authentication_error),
    (ForbiddenError, handle_forbidden_error),
    (django.http.Http404, handle_not_found_error),
    (ConflictError, handle_conflict_error),
    (Exception, handle_unknown_exception),
]
