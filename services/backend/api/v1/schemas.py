from http import HTTPStatus as status
from typing import Any

from ninja import Schema


class BadRequestError(Schema):
    detail: Any


class UnauthorizedError(Schema):
    detail: str = status.UNAUTHORIZED.phrase


class ForbiddenError(Schema):
    detail: str = status.FORBIDDEN.phrase


class NotFoundError(Schema):
    detail: str = status.NOT_FOUND.phrase


class ConflictError(Schema):
    detail: Any
