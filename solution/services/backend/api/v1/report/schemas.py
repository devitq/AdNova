from typing import ClassVar
from uuid import UUID

from ninja import ModelSchema, Schema

from apps.campaign.models import CampaignReport


class SubmitReportIn(ModelSchema):
    client_id: UUID

    class Meta:
        model = CampaignReport
        fields: ClassVar[tuple[str]] = (CampaignReport.message.field.name,)


class SubmitReportOut(Schema):
    status: str = "ok"
