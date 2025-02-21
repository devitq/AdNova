from django.test import TestCase, override_settings

from apps.advertiser.models import Advertiser
from apps.campaign.models import Campaign, CampaignReport
from apps.client.models import Client
from config.errors import ConflictError


class CampaignReportModelTest(TestCase):
    @classmethod
    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def setUpTestData(cls) -> None:
        cls.advertiser = Advertiser.objects.create(name="Test Advertiser")
        cls.campaign = Campaign.objects.create(
            advertiser=cls.advertiser,
            impressions_limit=1000,
            clicks_limit=500,
            cost_per_impression=0.05,
            cost_per_click=0.10,
            ad_title="Test Campaign",
            ad_text="This is a test campaign.",
            start_date=1,
            end_date=10,
        )
        cls.client_instance = Client.objects.create(
            login="test_client",
            age=30,
            gender="MALE",
            location="Test Location",
        )

    def test_campaign_report_creation(self) -> None:
        report = CampaignReport.objects.create(
            campaign=self.campaign,
            client=self.client_instance,
            state=CampaignReport.CampaignReportState.SENT,
            message="Inappropriate content",
            flagged_by_llm=True,
        )

        self.assertIsInstance(report, CampaignReport)
        self.assertEqual(report.campaign, self.campaign)
        self.assertEqual(report.client, self.client_instance)
        self.assertEqual(report.state, CampaignReport.CampaignReportState.SENT)
        self.assertEqual(report.message, "Inappropriate content")
        self.assertTrue(report.flagged_by_llm)

    def test_campaign_report_unique_together_constraint(self) -> None:
        CampaignReport.objects.create(
            campaign=self.campaign,
            client=self.client_instance,
            state=CampaignReport.CampaignReportState.SENT,
        )

        with self.assertRaises(ConflictError):
            CampaignReport.objects.create(
                campaign=self.campaign,
                client=self.client_instance,
                state=CampaignReport.CampaignReportState.UNDER_REVIEW,
            )
