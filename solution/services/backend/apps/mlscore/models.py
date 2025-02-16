from django.db import models

from apps.advertiser.models import Advertiser
from apps.client.models import Client
from apps.core.models import BaseModel


class Mlscore(BaseModel):
    advertiser = models.ForeignKey(
        Advertiser,
        on_delete=models.CASCADE,
        related_name="mlscores",
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="mlscores",
    )
    score = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f"{self.advertiser.name} | {self.client.login}"

    class Meta:
        unique_together = (
            "advertiser",
            "client",
        )
