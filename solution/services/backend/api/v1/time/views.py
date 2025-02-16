from http import HTTPStatus as status

from django.core.cache import cache
from django.http import HttpRequest
from ninja import Router

from api.v1 import schemas as global_schemas
from api.v1.time import schemas

router = Router(tags=["time"])


@router.post(
    "/advance",
    response={
        status.OK: schemas.CurrentDate,
        status.BAD_REQUEST: global_schemas.BadRequestError,
    },
)
def advance_time(
    request: HttpRequest, new_date: schemas.CurrentDate
) -> tuple[status, schemas.CurrentDate]:
    cache.set("current_date", new_date.current_date)

    return status.OK, new_date
