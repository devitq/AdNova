import random
from decimal import ROUND_HALF_UP, Decimal
from logging import Logger
from typing import Any, Self
from uuid import UUID

from django.conf import settings
from django.core.cache import cache
from django.core.validators import (
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
)
from django.db import models

from apps.advertiser.models import Advertiser
from apps.campaign.validators import (
    CampaignAgeValidator,
    CampaignDurationValidator,
    CampaignLimitsValidator,
    CampaignReportMessageValidator,
    CampaignStartDateValidator,
    CampaignTargetingGenderValidator,
    CampaignTargetingLocationValidator,
)
from apps.client.models import Client
from apps.core.models import BaseModel
from config.errors import ConflictError, ForbiddenError

logger: Logger = settings.LOGGER


class Campaign(BaseModel):
    class GenderChoices(models.TextChoices):
        MALE = "MALE", "MALE"
        FEMALE = "FEMALE", "FEMALE"
        ALL = "ALL", "ALL"

    def ad_image_directory_path(instance, filename: str) -> str:  # noqa: N805
        return f"campaigns/{instance.id}/{filename}"

    advertiser = models.ForeignKey(
        Advertiser,
        on_delete=models.CASCADE,
        related_name="campaigns",
    )

    impressions_limit = models.PositiveBigIntegerField()
    clicks_limit = models.PositiveBigIntegerField()
    cost_per_impression = models.FloatField(validators=[MinValueValidator(0)])
    cost_per_click = models.FloatField(validators=[MinValueValidator(0)])
    ad_title = models.TextField()
    ad_text = models.TextField()
    ad_image = models.ImageField(
        max_length=256,
        blank=True,
        null=True,
        upload_to=ad_image_directory_path,
    )
    start_date = models.PositiveIntegerField(db_index=True)
    end_date = models.PositiveIntegerField(db_index=True)

    gender = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        db_index=True,
        choices=GenderChoices,
    )
    age_from = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        db_index=True,
        validators=[MaxValueValidator(100)],
    )
    age_to = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        db_index=True,
        validators=[MaxValueValidator(100)],
    )
    location = models.TextField(
        blank=True,
        null=True,
        db_index=True,
        validators=[MinLengthValidator(1)],
    )

    READONLY_AFTER_START_FIELDS = (
        "impressions_limit",
        "clicks_limit",
        "start_date",
        "end_date",
    )

    def __str__(self) -> str:
        return self.ad_title

    def clean(self) -> None:
        CampaignTargetingGenderValidator()(self)
        CampaignTargetingLocationValidator()(self)
        CampaignAgeValidator()(self)
        CampaignDurationValidator()(self)
        CampaignLimitsValidator()(self)
        CampaignStartDateValidator()(self)

    def save(self, *args: Any, **kwargs: Any) -> None:
        created = self.pk is None

        super().save(*args, **kwargs)

        if created:
            self.setup_cache()

    def setup_cache(self) -> None:
        cache.add(
            f"campaign_{self.id}_impressions_count", self.impressions.count()
        )
        cache.add(f"campaign_{self.id}_clicks_count", self.clicks.count())
        cache.set(
            f"campaign_{self.id}_impressions_count", self.impressions.count()
        )
        cache.set(f"campaign_{self.id}_clicks_count", self.clicks.count())

    def inc_views(self) -> None:
        try:
            cache.incr(f"campaign_{self.id}_impressions_count", 1)
        except ValueError:
            self.setup_cache()
            logger.warning("Seems that %s missing caches", self.campaign_id)

    def inc_clicks(self) -> None:
        try:
            cache.incr(f"campaign_{self.id}_clicks_count", 1)
        except ValueError:
            self.setup_cache()
            logger.warning("Seems that %s missing caches", self.campaign_id)

    @property
    def ad_id(self) -> UUID:
        return self.id

    @property
    def campaign_id(self) -> UUID:
        return self.id

    @campaign_id.setter
    def campaign_id(self, value: UUID) -> None:
        self.id = value

    @property
    def started(self) -> bool:
        return isinstance(
            self.start_date, int
        ) and self.start_date <= cache.get("current_date", default=0)

    @property
    def active(self) -> bool:
        return (
            self.started
            and cache.get("current_date", default=0) <= self.end_date
        )

    @property
    def impressions_count(self) -> int:
        return cache.get(f"campaign_{self.id}_impressions_count", 0)

    @property
    def clicks_count(self) -> int:
        return cache.get(f"campaign_{self.id}_clicks_count", 0)

    def view(self, client: Client) -> None:
        try:
            CampaignImpression.objects.create(
                campaign_id=self.id,
                client_id=client.id,
                price=self.cost_per_impression,
                date=cache.get("current_date", default=0),
            )
            self.inc_views()
        except ConflictError:
            pass

    def click(self, client: Client) -> None:
        try:
            CampaignImpression.objects.get(campaign=self, client=client)
        except CampaignImpression.DoesNotExist:
            raise ForbiddenError from None

        try:
            CampaignClick.objects.create(
                campaign_id=self.id,
                client_id=client.id,
                price=self.cost_per_click,
                date=cache.get("current_date", default=0),
            )
            self.inc_clicks()
        except ConflictError:
            pass

    def get_statistics(self) -> dict[str, Any]:
        impressions = self.impressions.aggregate(
            total=models.Count("id"), spent=models.Sum("price")
        )
        clicks = self.clicks.aggregate(
            total=models.Count("id"), spent=models.Sum("price")
        )

        return self._calculate_metrics(impressions, clicks)

    def get_daily_statistics(self) -> list[dict[str, Any]]:
        last_click_date = self.clicks.aggregate(last_date=models.Max("date"))[
            "last_date"
        ]
        if not last_click_date:
            last_click_date = self.end_date

        current_day = cache.get("current_date", 0)
        start_day = self.start_date
        end_day = min(last_click_date, current_day)

        days_range = list(range(start_day, end_day + 1))

        impressions = self.impressions.values("date").annotate(
            total=models.Count("id"),
            spent=models.Sum("price", default=0.0),
        )
        clicks = self.clicks.values("date").annotate(
            total=models.Count("id"),
            spent=models.Sum("price", default=0.0),
        )

        imp_map = {imp["date"]: imp for imp in impressions}
        clk_map = {clk["date"]: clk for clk in clicks}

        daily_stats = []
        for day in days_range:
            imp = imp_map.get(day, {"total": 0, "spent": 0})
            clk = clk_map.get(day, {"total": 0, "spent": 0})

            metrics = self._calculate_metrics(imp, clk)
            metrics["date"] = day
            daily_stats.append(metrics)

        daily_stats.sort(key=lambda x: x["date"])

        return daily_stats

    @staticmethod
    def _calculate_metrics(
        impressions: dict[str, Any], clicks: dict[str, Any]
    ) -> dict[str, Any]:
        impressions_count = impressions.get("total", 0) or 0
        clicks_count = clicks.get("total", 0) or 0
        conversion = (
            (
                Decimal(str(clicks_count))
                / Decimal(str(impressions_count))
                * Decimal("100")
            )
            if impressions_count > 0
            else Decimal("0")
        )
        spent_impressions = Decimal(str(impressions.get("spent", 0) or 0))
        spent_clicks = Decimal(str(clicks.get("spent", 0) or 0))
        spent_total = spent_impressions + spent_clicks

        return {
            "impressions_count": impressions_count,
            "clicks_count": clicks_count,
            "conversion": float(
                conversion.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ),
            "spent_impressions": float(
                spent_impressions.quantize(
                    Decimal("0.000000001"), rounding=ROUND_HALF_UP
                )
            ),
            "spent_clicks": float(
                spent_clicks.quantize(
                    Decimal("0.000000001"), rounding=ROUND_HALF_UP
                )
            ),
            "spent_total": float(
                spent_total.quantize(
                    Decimal("0.000000001"), rounding=ROUND_HALF_UP
                )
            ),
        }

    @classmethod
    def get_available_campaigns(
        cls, client: Client
    ) -> models.manager.BaseManager[Self]:
        current_date = cache.get("current_date", default=0)

        date_filter = models.Q(start_date__lte=current_date) & models.Q(
            end_date__gte=current_date
        )
        location_filter = models.Q(location__isnull=True) | models.Q(
            location=client.location
        )
        gender_filter = (
            models.Q(gender__isnull=True)
            | models.Q(gender=cls.GenderChoices.ALL)
            | models.Q(gender=client.gender)
        )
        age_filter = (
            models.Q(age_from__lte=client.age)
            | models.Q(age_from__isnull=True)
        ) & (models.Q(age_to__gte=client.age) | models.Q(age_to__isnull=True))

        return cls.objects.filter(
            date_filter,
            location_filter,
            gender_filter,
            age_filter,
        ).only(
            Campaign.id.field.name,
            Campaign.advertiser_id.field.name,
            Campaign.impressions_limit.field.name,
            Campaign.clicks_limit.field.name,
            Campaign.cost_per_impression.field.name,
            Campaign.cost_per_click.field.name,
        )

    @classmethod
    def suggest(cls, client: Client) -> Self:
        campaigns = cls.get_available_campaigns(client)
        if not campaigns or campaigns == []:
            return None

        campaign_ids = [c.id for c in campaigns]

        client_impressions = CampaignImpression.objects.filter(
            client=client, campaign_id__in=campaign_ids
        ).values_list("campaign_id", flat=True)
        client_clicks = CampaignClick.objects.filter(
            client=client, campaign_id__in=campaign_ids
        ).values_list("campaign_id", flat=True)

        prioritized = []
        ml_values = []
        profit_values = []
        exceed_impressions_chance = (  # oh, can i just skip commenting this?
            *(0 for i in range(3)),
            *(1 for i in range(1)),
        )

        for campaign in campaigns:
            has_impression = campaign.id in client_impressions
            has_click = campaign.id in client_clicks
            campaign_impressions_count = campaign.impressions_count

            if not has_impression:
                allow_exceed_impressions = random.choice(
                    exceed_impressions_chance
                )
                impressions_limit = round(
                    campaign.impressions_limit
                    + campaign.impressions_limit
                    * 0.1
                    * allow_exceed_impressions
                )
                if campaign_impressions_count >= impressions_limit:
                    continue

            ml_score = cache.get(
                f"mlscore_{client.id}_{campaign.advertiser_id}", 0
            )
            ml_values.append(ml_score)

            if has_impression:
                profit = campaign.cost_per_click if not has_click else 0
            else:
                profit = campaign.cost_per_impression + campaign.cost_per_click

            profit_values.append(profit)

            remaining_imp = (
                campaign.impressions_limit - campaign_impressions_count
            )
            capacity_ratio = (
                remaining_imp / campaign.impressions_limit
                if campaign.impressions_limit > 0
                else 1
            )

            prioritized.append(
                (
                    campaign,
                    {
                        "profit": profit,
                        "ml": ml_score,
                        "capacity": 1 - capacity_ratio,
                    },
                )
            )

        if not ml_values or not profit_values:
            return None

        max_ml = max(ml_values)
        max_profit = max(profit_values)
        min_profit = min(profit_values)
        profit_range = (
            max_profit - min_profit if max_profit != min_profit else 1
        )

        final_list = []
        for campaign, metrics in prioritized:
            norm_profit = (metrics["profit"] - min_profit) / profit_range
            norm_ml = metrics["ml"] / max_ml if max_ml > 0 else 0

            priority = (
                0.8 * norm_profit + 0.2 * norm_ml + 0.1 * metrics["capacity"]
            )

            final_list.append((campaign, priority))

        final_list.sort(key=lambda x: -x[1])

        if len(final_list) != 0:
            campaign = final_list[0][0]

            return Campaign.objects.only(
                Campaign.id.field.name,
                Campaign.advertiser_id.field.name,
                Campaign.ad_title.field.name,
                Campaign.ad_text.field.name,
                Campaign.ad_image.field.name,
                Campaign.cost_per_impression.field.name,
                Campaign.cost_per_click.field.name,
            ).get(id=campaign.id)

        return None


class CampaignImpression(BaseModel):
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="impressions",
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="impressions",
    )
    price = models.FloatField()
    date = models.PositiveIntegerField(db_index=True)

    def __str__(self) -> str:
        return f"{self.client.login} > {self.campaign.ad_title}"

    class Meta:
        unique_together = (
            "campaign",
            "client",
        )


class CampaignClick(BaseModel):
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="clicks",
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="clicks",
    )
    price = models.FloatField()
    date = models.PositiveIntegerField(db_index=True)

    def __str__(self) -> str:
        return f"{self.client.login} > {self.campaign.ad_title}"

    class Meta:
        unique_together = (
            "campaign",
            "client",
        )


class CampaignReport(BaseModel):
    class CampaignReportState(models.TextChoices):
        SENT = "s", "Sent"
        UNDER_REVIEW = "r", "Under review"
        TOOK_ACTION = "t", "Took action"
        SKIPPED = "f", "Skipped"

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.SET_NULL,
        related_name="reports",
        blank=True,
        null=True,
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        related_name="reports",
        blank=True,
        null=True,
    )
    state = models.CharField(
        max_length=1,
        choices=CampaignReportState,
        default=CampaignReportState.SENT,
    )
    message = models.TextField(null=True, blank=True)
    flagged_by_llm = models.BooleanField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            "campaign",
            "client",
        )

    def __str__(self) -> str:
        login = self.client.login if self.client else "(client deleted)"
        ad_title = (
            self.campaign.ad_title if self.campaign else "(campaign deleted)"
        )
        return f"{login} > {ad_title}"

    def clean(self) -> None:
        CampaignReportMessageValidator()(self)
