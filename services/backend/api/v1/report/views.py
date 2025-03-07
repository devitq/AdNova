from http import HTTPStatus as status
from uuid import UUID

from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from api.v1 import schemas as global_schemas
from api.v1.report import schemas
from apps.campaign.models import Campaign, CampaignImpression, CampaignReport
from apps.campaign.tasks import moderate_campaign_task
from apps.client.models import Client
from config.errors import ForbiddenError

router = Router(tags=["report"])


@router.post(
    "/{campaign_id}",
    response={
        status.OK: schemas.SubmitReportOut,
        status.BAD_REQUEST: global_schemas.BadRequestError,
        status.FORBIDDEN: global_schemas.ForbiddenError,
        status.NOT_FOUND: global_schemas.NotFoundError,
        status.CONFLICT: global_schemas.ConflictError,
    },
)
def submit_report(
    request: HttpRequest, campaign_id: UUID, report: schemas.SubmitReportIn
) -> tuple[status, schemas.SubmitReportOut]:
    campaign = get_object_or_404(Campaign, id=campaign_id)
    client = get_object_or_404(Client, id=report.client_id)

    try:
        CampaignImpression.objects.get(campaign=campaign, client=client)
    except CampaignImpression.DoesNotExist:
        raise ForbiddenError from None

    report_instance = CampaignReport.objects.create(
        campaign=campaign,
        client=client,
        message=report.message,
    )
    moderate_campaign_task.delay(
        report_instance.id, campaign.ad_title, campaign.ad_text
    )

    return status.OK, schemas.SubmitReportOut()
