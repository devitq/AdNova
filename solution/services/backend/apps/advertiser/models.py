from uuid import UUID

from decimal import Decimal, ROUND_HALF_UP
from django.core.cache import cache
from django.db import models

from apps.core.models import BaseModel


class Advertiser(BaseModel):
    name = models.TextField()

    def __str__(self) -> str:
        return self.name

    @property
    def advertiser_id(self) -> UUID:
        return self.id

    @advertiser_id.setter
    def advertiser_id(self, value: UUID) -> None:
        self.id = value

    def get_statistics(self) -> dict[str, int | float]:
        campaigns = self.campaigns.all()

        total_impressions = 0
        total_clicks = 0
        total_spent_impressions = Decimal("0.0")
        total_spent_clicks = Decimal("0.0")

        for campaign in campaigns:
            stats = campaign.get_statistics()
            total_impressions += stats["impressions_count"]
            total_clicks += stats["clicks_count"]
            total_spent_impressions += Decimal(str(stats["spent_impressions"]))
            total_spent_clicks += Decimal(str(stats["spent_clicks"]))

        total_spent = total_spent_impressions + total_spent_clicks
        conversion = (
            (
                Decimal(str(total_clicks))
                / Decimal(str(total_impressions))
                * Decimal("100")
            )
            if total_impressions > 0
            else Decimal("0")
        )

        return {
            "impressions_count": total_impressions,
            "clicks_count": total_clicks,
            "conversion": float(
                conversion.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ),
            "spent_impressions": float(
                total_spent_impressions.quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            ),
            "spent_clicks": float(
                total_spent_clicks.quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            ),
            "spent_total": float(
                total_spent.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ),
        }

    def get_daily_statistics(self) -> list[dict[str, int | float]]:
        campaigns = self.campaigns.all()

        daily_stats_map = {}

        for campaign in campaigns:
            daily_stats = campaign.get_daily_statistics()
            for stat in daily_stats:
                date = stat["date"]
                if date not in daily_stats_map:
                    daily_stats_map[date] = {
                        "impressions_count": 0,
                        "clicks_count": 0,
                        "spent_impressions": Decimal("0.0"),
                        "spent_clicks": Decimal("0.0"),
                    }

                daily_stats_map[date]["impressions_count"] += stat[
                    "impressions_count"
                ]
                daily_stats_map[date]["clicks_count"] += stat["clicks_count"]
                daily_stats_map[date]["spent_impressions"] += Decimal(
                    str(stat["spent_impressions"])
                )
                daily_stats_map[date]["spent_clicks"] += Decimal(
                    str(stat["spent_clicks"])
                )

        days_range = range(cache.get("current_date", 0) + 1)

        for day in days_range:
            if day not in daily_stats_map:
                daily_stats_map[day] = {
                    "impressions_count": 0,
                    "clicks_count": 0,
                    "spent_impressions": Decimal("0.0"),
                    "spent_clicks": Decimal("0.0"),
                }

        daily_stats = []
        for date, metrics in daily_stats_map.items():
            total_spent = (
                metrics["spent_impressions"] + metrics["spent_clicks"]
            )
            conversion = (
                Decimal(str(metrics["clicks_count"]))
                / Decimal(str(metrics["impressions_count"]))
                * Decimal("100")
                if metrics["impressions_count"] > 0
                else Decimal("0")
            )

            daily_stats.append({
                "date": date,
                "impressions_count": metrics["impressions_count"],
                "clicks_count": metrics["clicks_count"],
                "conversion": float(
                    conversion.quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                ),
                "spent_impressions": float(
                    metrics["spent_impressions"].quantize(
                        Decimal("0.0000000001"), rounding=ROUND_HALF_UP
                    )
                ),
                "spent_clicks": float(
                    metrics["spent_clicks"].quantize(
                        Decimal("0.0000000001"), rounding=ROUND_HALF_UP
                    )
                ),
                "spent_total": float(
                    total_spent.quantize(
                        Decimal("0.0000000001"), rounding=ROUND_HALF_UP
                    )
                ),
            })

        return sorted(daily_stats, key=lambda item: item["date"])
