import contextlib
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Self
from uuid import UUID

from django.core.cache import cache
from django.core.exceptions import ValidationError
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
    CampaignTargetingLocationValidator,
)
from apps.client.models import Client
from apps.core.models import BaseModel
from apps.mlscore.models import Mlscore
from config.errors import ConflictError, ForbiddenError


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
        CampaignTargetingLocationValidator()(self)
        CampaignAgeValidator()(self)
        CampaignDurationValidator()(self)
        CampaignLimitsValidator()(self)

        current_date = cache.get("current_date", default=0)

        err = "start_date must be greater than the current date."

        try:
            original = Campaign.objects.get(id=self.id or "")
            if (
                original.start_date != self.start_date
                and self.start_date < current_date
            ):
                raise ValidationError(err)
        except Campaign.DoesNotExist:
            if self.start_date < current_date:
                raise ValidationError(err) from None

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

    def view(self, client: Client) -> None:
        with contextlib.suppress(ConflictError):
            CampaignImpression.objects.create(
                campaign=self,
                client=client,
                price=self.cost_per_impression,
                date=cache.get("current_date", default=0),
            )

    def click(self, client: Client) -> None:
        if not self.active:
            err = "Can't click on inactive campaign."
            raise ForbiddenError(err)

        try:
            CampaignImpression.objects.get(campaign=self, client=client)
        except CampaignImpression.DoesNotExist:
            raise ForbiddenError from None

        with contextlib.suppress(ConflictError):
            CampaignClick.objects.create(
                campaign=self,
                client=client,
                price=self.cost_per_click,
                date=cache.get("current_date", default=0),
            )

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

        return (
            cls.objects.filter(
                date_filter,
                location_filter,
                gender_filter,
                age_filter,
            )
            .select_related("advertiser")
            .prefetch_related("clicks", "impressions", "advertiser__mlscores")
        )

    @classmethod
    def suggest(cls, client: Client) -> Self:
        base_campaigns = cls.get_available_campaigns(client)
        if not base_campaigns or base_campaigns == []:
            return None

        advertiser_ids = list({c.advertiser_id for c in base_campaigns})
        ml_scores = Mlscore.objects.filter(
            client=client, advertiser_id__in=advertiser_ids
        ).values("advertiser_id", "score")
        ml_dict = {m["advertiser_id"]: m["score"] for m in ml_scores}

        campaigns = list(
            base_campaigns.annotate(
                impressions_count=models.Count("impressions"),
                clicks_count=models.Count("clicks"),
            )
        )
        campaign_ids = [c.id for c in campaigns]

        client_impressions = set(
            CampaignImpression.objects.filter(
                client=client, campaign_id__in=campaign_ids
            ).values_list("campaign_id", flat=True)
        )
        client_clicks = set(
            CampaignClick.objects.filter(
                client=client, campaign_id__in=campaign_ids
            ).values_list("campaign_id", flat=True)
        )

        prioritized = []
        ml_values = []
        profit_values = []

        for campaign in campaigns:
            if campaign.impressions_count >= campaign.impressions_limit:
                continue

            ml_score = ml_dict.get(campaign.advertiser_id, 0)
            ml_values.append(ml_score)

            has_impression = campaign.id in client_impressions
            has_click = campaign.id in client_clicks

            if has_impression:
                profit = campaign.cost_per_click if not has_click else 0
            else:
                profit = campaign.cost_per_impression + campaign.cost_per_click
            print(profit)
            if profit <= 0:
                continue

            profit_values.append(profit)

            remaining_imp = (
                campaign.impressions_limit - campaign.impressions_count
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

        max_ml = max(ml_values) if ml_values else 1
        max_profit = max(profit_values) if profit_values else 1
        min_profit = min(profit_values) if profit_values else 0
        profit_range = (
            max_profit - min_profit if max_profit != min_profit else 1
        )

        print(prioritized, max_ml, max_profit, min_profit, profit_range)

        final_list = []
        for campaign, metrics in prioritized:
            norm_profit = (metrics["profit"] - min_profit) / profit_range
            norm_ml = metrics["ml"] / max_ml if max_ml > 0 else 0

            priority = (
                0.5 * norm_profit + 0.25 * norm_ml + 0.15 * metrics["capacity"]
            )

            final_list.append((campaign, priority))

        final_list.sort(key=lambda x: -x[1])
        return final_list[0][0] if len(final_list) >= 1 else None


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
