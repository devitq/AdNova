from typing import Annotated, Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, NonNegativeFloat, NonNegativeInt


class BadRequestError(BaseModel):
    detail: Any


class ForbiddenError(BaseModel):
    detail: str = "Forbidden"


class NotFoundError(BaseModel):
    detail: str = "Not Found"


class CampaignTargeting(BaseModel):
    gender: Literal["MALE", "FEMALE", "ALL"] | None = None
    age_from: Annotated[NonNegativeInt, Field(strict=True, ls=100)] | None = (
        None
    )
    age_to: Annotated[NonNegativeInt, Field(strict=True, ls=100)] | None = None
    location: str | None = None


class CampaignCreateIn(BaseModel):
    targeting: CampaignTargeting
    ad_title: str
    ad_text: str
    impressions_limit: NonNegativeInt
    clicks_limit: NonNegativeInt
    cost_per_impression: NonNegativeFloat
    cost_per_click: NonNegativeFloat
    start_date: NonNegativeInt
    end_date: NonNegativeInt


class CampaignUpdateIn(CampaignCreateIn):
    pass


class CampaignOut(BaseModel):
    campaign_id: str
    advertiser_id: str
    targeting: CampaignTargeting
    ad_title: str
    ad_text: str
    ad_image: str | None = None
    impressions_limit: NonNegativeInt
    clicks_limit: NonNegativeInt
    cost_per_impression: NonNegativeFloat
    cost_per_click: NonNegativeFloat
    start_date: NonNegativeInt
    end_date: NonNegativeInt


class Advertiser(BaseModel):
    advertiser_id: UUID
    name: str


class Stat(BaseModel):
    impressions_count: int
    clicks_count: int
    conversion: float
    spent_impressions: float
    spent_clicks: float
    spent_total: float


class DailyStat(Stat):
    date: int


class GenerateAdTextIn(BaseModel):
    advertiser_name: str
    ad_title: str


class GenerateAdTextResult(BaseModel):
    task_id: str
    status: str
    result: str
