from http import HTTPStatus as status

from django.core.exceptions import ValidationError


class ConflictError(Exception):
    def __init__(self, validation_error: ValidationError) -> None:
        self.validation_error = validation_error


class ForbiddenError(Exception):
    def __init__(self, message: str = status.FORBIDDEN.phrase) -> None:
        self.message = message
