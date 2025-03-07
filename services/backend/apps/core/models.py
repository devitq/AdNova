import uuid
from typing import Any

from django.core.exceptions import ValidationError
from django.db import models

from config.errors import ConflictError


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.validate()

        super().save(*args, **kwargs)

    def validate(
        self,
        validate_unique: bool = True,
        validate_constraints: bool = True,
        include: list[models.Field] | None = None,
    ) -> None:
        self.full_clean(
            validate_unique=False,
            validate_constraints=False,
            exclude=(
                field.name
                for field in set(self._meta.get_fields()) - set(include)
            )
            if include
            else None,
        )

        if validate_unique:
            try:
                self.validate_unique()
            except ValidationError as e:
                raise ConflictError(e) from None

        if validate_constraints:
            try:
                self.validate_constraints()
            except ValidationError as e:
                raise ConflictError(e) from None
