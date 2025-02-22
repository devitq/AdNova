from http import HTTPStatus as status
from uuid import UUID

from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import File, Query, Router
from ninja.errors import HttpError
from ninja.files import UploadedFile
from PIL import Image

from api.v1 import schemas as global_schemas
from api.v1.campaigns import schemas, utils
from apps.advertiser.models import Advertiser
from apps.campaign.models import Campaign
from config.errors import ForbiddenError

router = Router(tags=["campaigns"])


@router.post(
    "/{advertiser_id}/campaigns",
    response={
        status.CREATED: schemas.CampaignOut,
        status.BAD_REQUEST: global_schemas.BadRequestError,
        status.NOT_FOUND: global_schemas.NotFoundError,
    },
)
def create_campaign(
    request: HttpRequest, advertiser_id: UUID, data: schemas.CampaignCreateIn
) -> tuple[status, schemas.CampaignOut]:
    advertiser = get_object_or_404(Advertiser, id=advertiser_id)

    campaign = Campaign.objects.create(
        advertiser_id=advertiser.id,
        **data.dict(exclude={"targeting"}),
        **data.targeting.dict() if data.targeting else {},
    )

    return status.CREATED, utils.normalize_campaign(campaign)


@router.get(
    "/{advertiser_id}/campaigns",
    response={
        status.OK: list[schemas.CampaignOut],
        status.BAD_REQUEST: global_schemas.BadRequestError,
        status.NOT_FOUND: global_schemas.NotFoundError,
    },
)
def list_campaigns(
    request: HttpRequest,
    advertiser_id: UUID,
    filters: Query[schemas.CampaignListFilters],
) -> tuple[status, list[schemas.CampaignOut]]:
    advertaiser = get_object_or_404(Advertiser, id=advertiser_id)
    campaigns = Campaign.objects.filter(advertiser=advertaiser).order_by(
        "-end_date"
    )
    paginated_campaigns = campaigns[
        (filters.page - 1) * filters.size : filters.page * filters.size
    ]

    return status.OK, [
        utils.normalize_campaign(campaign) for campaign in paginated_campaigns
    ]


@router.get(
    "/{advertiser_id}/campaigns/{campaign_id}",
    response={
        status.OK: schemas.CampaignOut,
        status.BAD_REQUEST: global_schemas.BadRequestError,
        status.NOT_FOUND: global_schemas.NotFoundError,
    },
)
def get_campaign(
    request: HttpRequest, advertiser_id: UUID, campaign_id: UUID
) -> tuple[status, schemas.CampaignOut]:
    return status.OK, utils.normalize_campaign(
        get_object_or_404(
            Campaign,
            id=campaign_id,
            advertiser_id=advertiser_id,
        )
    )


@router.put(
    "/{advertiser_id}/campaigns/{campaign_id}",
    response={
        status.OK: schemas.CampaignOut,
        status.BAD_REQUEST: global_schemas.BadRequestError,
        status.FORBIDDEN: global_schemas.ForbiddenError,
        status.NOT_FOUND: global_schemas.NotFoundError,
    },
)
def update_campaign(
    request: HttpRequest,
    advertiser_id: UUID,
    campaign_id: UUID,
    data: schemas.CampaignUpdateIn,
) -> tuple[status, schemas.CampaignOut]:
    campaign = get_object_or_404(
        Campaign,
        id=campaign_id,
        advertiser_id=advertiser_id,
    )

    for attr, value in data.dict().items():
        if attr == "targeting":
            for t_attr, t_value in value.items():
                setattr(campaign, t_attr, t_value)
        elif not (
            attr in Campaign.READONLY_AFTER_START_FIELDS
            and campaign.started
            and getattr(campaign, attr) != value
        ):
            setattr(campaign, attr, value)
        else:
            raise ForbiddenError

    campaign.save()

    return status.OK, utils.normalize_campaign(campaign)


@router.delete(
    "/{advertiser_id}/campaigns/{campaign_id}",
    response={
        status.NO_CONTENT: None,
        status.BAD_REQUEST: global_schemas.BadRequestError,
        status.NOT_FOUND: global_schemas.NotFoundError,
    },
)
def delete_campaign(
    request: HttpRequest, advertiser_id: UUID, campaign_id: UUID
) -> tuple[status, None]:
    campaign = get_object_or_404(
        Campaign,
        id=campaign_id,
        advertiser_id=advertiser_id,
    )

    if campaign.ad_image:
        campaign.ad_image.delete()

    campaign.delete()

    return status.NO_CONTENT, None


@router.post(
    "/{advertiser_id}/campaigns/{campaign_id}/ad_image",
    response={
        status.OK: schemas.CampaignOut,
        status.BAD_REQUEST: global_schemas.BadRequestError,
        status.NOT_FOUND: global_schemas.NotFoundError,
    },
    description=(
        "Uploads image to ad_image field. "
        "If image already exists then image will be overridden."
    ),
)
def upload_ad_image(
    request: HttpRequest,
    advertiser_id: UUID,
    campaign_id: UUID,
    ad_image: UploadedFile = File(...),  # noqa: B008
) -> tuple[status, Campaign]:
    campaign = get_object_or_404(
        Campaign,
        id=campaign_id,
        advertiser_id=advertiser_id,
    )
    if ad_image.size >= 10 * 1024 * 1024:
        raise HttpError(
            status.BAD_REQUEST, "File can't be bigger than 10MB."
        )
    try:
        Image.open(ad_image).verify()
    except (OSError, SyntaxError):
        raise HttpError(
            status.BAD_REQUEST, "File must be a valid image."
        ) from None
    if campaign.ad_image:
        campaign.ad_image.delete(save=True)
    campaign.ad_image = ad_image
    campaign.save()

    return status.OK, campaign


@router.delete(
    "/{advertiser_id}/campaigns/{campaign_id}/ad_image",
    response={
        status.NO_CONTENT: None,
        status.BAD_REQUEST: global_schemas.BadRequestError,
        status.NOT_FOUND: global_schemas.NotFoundError,
    },
    description=(
        "Deletes image from ad_image field. "
        "If no image exists still returns 204."
    ),
)
def delete_ad_image(
    request: HttpRequest, advertiser_id: UUID, campaign_id: UUID
) -> tuple[status, None]:
    campaign = get_object_or_404(
        Campaign,
        id=campaign_id,
        advertiser_id=advertiser_id,
    )
    if campaign.ad_image:
        campaign.ad_image.delete(save=True)

    return status.NO_CONTENT, None
