from typing import Any

from django.core.management.base import BaseCommand

from apps.campaign.models import Campaign
from apps.mlscore.models import Mlscore


class Command(BaseCommand):
    help = (
        "Initialize cache with current counts of "
        "impressions, clicks, and ML scores."
    )

    def handle(self, *args: Any, **kwargs: Any) -> None:
        for campaign in Campaign.objects.all():
            campaign.setup_cache()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Initialized cache for Campaign {campaign.id}: "
                    f"{campaign.impressions_count} impressions, "
                    f"{campaign.clicks_count} clicks."
                )
            )

        for mlscore in Mlscore.objects.all():
            mlscore.setup_cache()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Initialized cache for MLscore: "
                    f"Client {mlscore.client_id}, "
                    f"Advertiser {mlscore.advertiser_id}, "
                    f"Score {mlscore.score}."
                )
            )
