from api.v1.campaigns import schemas
from apps.campaign.models import Campaign


def normalize_campaign(campaign: Campaign) -> schemas.CampaignOut:
    campaign.targeting = schemas.CampaignTargeting.from_orm(campaign)
    return schemas.CampaignOut.from_orm(campaign)
