from uuid import UUID

from django.core.validators import MaxValueValidator
from django.db import models

from apps.core.models import BaseModel


class Client(BaseModel):
    class GenderChoices(models.TextChoices):
        MALE = "MALE", "MALE"
        FEMALE = "FEMALE", "FEMALE"

    login = models.TextField()
    age = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)])
    location = models.TextField()
    gender = models.CharField(max_length=6, choices=GenderChoices)

    def __str__(self) -> str:
        return self.login

    @property
    def client_id(self) -> UUID:
        return self.id

    @client_id.setter
    def client_id(self, value: UUID) -> None:
        self.id = value
