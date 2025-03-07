from typing import Any


class HTTPError(Exception):
    pass


class BadRequestError(HTTPError):
    def __init__(self, detail: Any) -> None:
        super().__init__(f"Bad Request: {detail}")
        self.detail = detail


class ForbiddenError(HTTPError):
    def __init__(self, detail: str = "Forbidden") -> None:
        super().__init__(f"Forbidden: {detail}")
        self.detail = detail


class NotFoundError(HTTPError):
    def __init__(self, detail: str = "Not Found") -> None:
        super().__init__(f"Not Found: {detail}")
        self.detail = detail
