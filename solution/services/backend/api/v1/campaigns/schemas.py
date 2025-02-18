import typing
from typing import Any
from uuid import UUID

from ninja import ModelSchema, Schema
from pydantic import field_validator
from pydantic.types import NonNegativeInt, PositiveInt

from apps.campaign.models import Campaign


class CampaignTargeting(ModelSchema):
    class Meta:
        model = Campaign
        fields: typing.ClassVar[tuple[str]] = (
            Campaign.gender.field.name,
            Campaign.age_from.field.name,
            Campaign.age_to.field.name,
            Campaign.location.field.name,
        )
        fields_optional = "__all__"


class CampaignOut(ModelSchema):
    campaign_id: UUID
    advertiser_id: UUID
    targeting: CampaignTargeting = None

    class Meta:
        model = Campaign
        fields: typing.ClassVar[tuple[str]] = (
            Campaign.ad_title.field.name,
            Campaign.ad_text.field.name,
            Campaign.ad_image.field.name,
            Campaign.impressions_limit.field.name,
            Campaign.clicks_limit.field.name,
            Campaign.cost_per_impression.field.name,
            Campaign.cost_per_click.field.name,
            Campaign.start_date.field.name,
            Campaign.end_date.field.name,
        )


class CampaignCreateIn(ModelSchema):
    targeting: CampaignTargeting = None

    class Meta:
        model = Campaign
        fields: typing.ClassVar[tuple[str]] = (
            Campaign.ad_title.field.name,
            Campaign.ad_text.field.name,
            Campaign.impressions_limit.field.name,
            Campaign.clicks_limit.field.name,
            Campaign.cost_per_impression.field.name,
            Campaign.cost_per_click.field.name,
            Campaign.start_date.field.name,
            Campaign.end_date.field.name,
        )

    @field_validator("targeting", mode="before")
    @classmethod
    def validate_target(cls, value: Any) -> Any:
        if (
            not isinstance(value, dict)
            and not isinstance(
                value,
                CampaignTargeting,
            )
            and value
        ):
            err = "The 'targeting' field must be a valid object or null."
            raise ValueError(err)
        return value


class CampaignUpdateIn(ModelSchema):
    targeting: CampaignTargeting = None

    class Meta:
        model = Campaign
        fields: typing.ClassVar[tuple[str]] = (
            Campaign.impressions_limit.field.name,
            Campaign.clicks_limit.field.name,
            Campaign.ad_title.field.name,
            Campaign.ad_text.field.name,
            Campaign.cost_per_impression.field.name,
            Campaign.cost_per_click.field.name,
            Campaign.start_date.field.name,
            Campaign.end_date.field.name,
        )

    @field_validator("targeting", mode="before")
    @classmethod
    def validate_target(cls, value: Any) -> Any:
        if (
            not isinstance(value, dict)
            and not isinstance(
                value,
                CampaignTargeting,
            )
            and value
        ):
            err = "The 'targeting' field must be a valid object or null."
            raise ValueError(err)
        return value


class CampaignListFilters(Schema):
    page: PositiveInt = 1
    size: NonNegativeInt = 100
