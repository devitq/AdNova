import typing

from ninja import ModelSchema, Schema

from apps.campaign.models import CampaignReport


class SubmitReportIn(ModelSchema):
    class Meta:
        model = CampaignReport
        fields: typing.ClassVar[tuple[str]] = (
            CampaignReport.client.field.name,
            CampaignReport.message.field.name,
        )


class SubmitReportOut(Schema):
    status: str = "ok"
