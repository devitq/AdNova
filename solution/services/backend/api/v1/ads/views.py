from http import HTTPStatus as status
from uuid import UUID

from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from api.v1 import schemas as global_schemas
from api.v1.ads import schemas
from apps.campaign.models import Campaign
from apps.client.models import Client

router = Router(tags=["ads"])


@router.get(
    "",
    response={
        status.OK: schemas.Advertisment,
        status.BAD_REQUEST: global_schemas.BadRequestError,
        status.NOT_FOUND: global_schemas.NotFoundError,
    },
)
def get_advertisment(
    request: HttpRequest, client_id: UUID
) -> tuple[status, Campaign]:
    client = get_object_or_404(Client, id=client_id)

    campaign = Campaign.suggest(client)

    campaign.view(client)

    return status.OK, campaign


@router.post(
    "/{advertisment_id}/click",
    response={
        status.NO_CONTENT: None,
        status.BAD_REQUEST: global_schemas.BadRequestError,
        status.FORBIDDEN: global_schemas.ForbiddenError,
        status.NOT_FOUND: global_schemas.NotFoundError,
    },
)
def click_on_advertisment(
    request: HttpRequest, advertisment_id: UUID, client: schemas.ClickIn
) -> tuple[status, None]:
    campaign_instance: Campaign = get_object_or_404(
        Campaign, id=advertisment_id
    )
    client_instance: Client = get_object_or_404(Client, id=client.client_id)

    campaign_instance.click(client_instance)

    return status.NO_CONTENT, None
