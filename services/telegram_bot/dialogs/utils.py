from api.schemas import CampaignCreateIn, CampaignTargeting


def campaign_from_list(fields: list[str]) -> CampaignCreateIn:
    return CampaignCreateIn(
        targeting=CampaignTargeting(
            gender=None if fields[8] == "None" else fields[8],
            age_from=None if fields[9] == "None" else fields[9],
            age_to=None if fields[10] == "None" else fields[10],
            location=None if fields[11] == "None" else fields[11],
        ),
        ad_title=fields[0],
        ad_text=fields[1],
        impressions_limit=fields[2],
        clicks_limit=fields[3],
        cost_per_impression=fields[4],
        cost_per_click=fields[5],
        start_date=fields[6],
        end_date=fields[7],
    )
