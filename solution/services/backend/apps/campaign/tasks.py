import contextlib
from concurrent.futures import ThreadPoolExecutor

from celery import shared_task

from apps.campaign.models import CampaignReport
from integrations.yandexai.generators.ad_text import YandexAIAdTextGenerator
from integrations.yandexai.moderation import YandexAIModerator


@shared_task
def generate_ad_text_task(advertiser_name: str, ad_title: str) -> str | None:
    return YandexAIAdTextGenerator().generate_ad_text(
        advertiser_name, ad_title
    )


@shared_task(ignore_result=True)
def moderate_campaign_task(
    report_id: int, ad_title: str, ad_text: str
) -> None:
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_text = executor.submit(
            YandexAIModerator().get_moderation_verdict, ad_text
        )
        future_title = executor.submit(
            YandexAIModerator().get_moderation_verdict, ad_title
        )

        ad_text_verdict = future_text.result()
        ad_title_verdict = future_title.result()

    overall_verdict = ad_title_verdict or ad_text_verdict

    with contextlib.suppress(CampaignReport.DoesNotExist):
        report = CampaignReport.objects.get(id=report_id)
        report.flagged_by_llm = overall_verdict
        report.save()
