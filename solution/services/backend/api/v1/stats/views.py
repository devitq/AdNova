from http import HTTPStatus as status
from typing import Any
from uuid import UUID

from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from api.v1 import schemas as global_schemas
from api.v1.stats import schemas
from apps.campaign.models import Advertiser, Campaign

router = Router(tags=["stats"])


@router.get(
    "/campaigns/{campaign_id}",
    response={
        status.OK: schemas.Stat,
        status.BAD_REQUEST: global_schemas.BadRequestError,
        status.NOT_FOUND: global_schemas.NotFoundError,
    },
)
def get_campaign_statistics(
    request: HttpRequest, campaign_id: UUID
) -> tuple[status, dict[str, Any]]:
    campaign = get_object_or_404(Campaign, id=campaign_id)

    return status.OK, campaign.get_statistics()


@router.get(
    "/campaigns/{campaign_id}/daily",
    response={
        status.OK: list[schemas.DailyStat],
        status.BAD_REQUEST: global_schemas.BadRequestError,
        status.NOT_FOUND: global_schemas.NotFoundError,
    },
)
def get_daily_campaign_statistics(
    request: HttpRequest, campaign_id: UUID
) -> tuple[status, dict[str, Any]]:
    campaign = get_object_or_404(Campaign, id=campaign_id)

    return status.OK, campaign.get_daily_statistics()


@router.get(
    "/advertisers/{advertiser_id}",
    response={
        status.OK: schemas.Stat,
        status.BAD_REQUEST: global_schemas.BadRequestError,
        status.NOT_FOUND: global_schemas.NotFoundError,
    },
)
def get_advertiser_statistics(
    request: HttpRequest, advertiser_id: UUID
) -> tuple[status, dict[str, Any]]:
    advertiser = get_object_or_404(Advertiser, id=advertiser_id)

    return status.OK, advertiser.get_statistics()


@router.get(
    "/advertisers/{advertiser_id}/campaigns/daily",
    response={
        status.OK: list[schemas.DailyStat],
        status.BAD_REQUEST: global_schemas.BadRequestError,
        status.NOT_FOUND: global_schemas.NotFoundError,
    },
)
def get_daily_advertiser_statistics(
    request: HttpRequest, advertiser_id: UUID
) -> tuple[status, dict[str, Any]]:
    advertiser = get_object_or_404(Advertiser, id=advertiser_id)

    return status.OK, advertiser.get_daily_statistics()
