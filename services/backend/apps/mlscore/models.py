from typing import Any

from django.core.cache import cache
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

    def save(self, *args: Any, **kwargs: Any) -> None:
        super().save(*args, **kwargs)

        self.setup_cache()

    def setup_cache(self) -> None:
        cache.add(f"mlscore_{self.client_id}_{self.advertiser_id}", self.score)
        cache.set(f"mlscore_{self.client_id}_{self.advertiser_id}", self.score)

    class Meta:
        unique_together = (
            "advertiser",
            "client",
        )
