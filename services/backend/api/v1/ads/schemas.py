from typing import ClassVar
from uuid import UUID

from ninja import ModelSchema, Schema

from apps.campaign.models import Campaign


class Advertisment(ModelSchema):
    advertiser_id: UUID
    ad_id: UUID

    class Meta:
        model = Campaign
        fields: ClassVar[tuple[str]] = (
            Campaign.ad_title.field.name,
            Campaign.ad_text.field.name,
            Campaign.ad_image.field.name,
        )


class ClickIn(Schema):
    client_id: UUID
