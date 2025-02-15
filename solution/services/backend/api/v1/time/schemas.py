from django.core.cache import cache
from ninja import Schema
from pydantic import field_validator
from pydantic.types import NonNegativeInt


class CurrentDate(Schema):
    current_date: NonNegativeInt

    @field_validator("current_date", mode="after")
    @classmethod
    def check_bigger_than_setted_date(cls, value: int) -> int:
        current_date = cache.get("current_date", default=0)
        if value < current_date:
            err = (
                "current_date can't be less than setted "
                f"date ({current_date})."
            )
            raise ValueError(err)

        return value
