from django.test import TestCase, override_settings

from apps.advertiser.models import Advertiser
from apps.campaign.models import Campaign, CampaignImpression
from apps.client.models import Client
from config.errors import ConflictError


class CampaignImpressionModelTest(TestCase):
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
            login="test_client", age=15, location="Moscow", gender="FEMALE"
        )
        cls.impression = CampaignImpression.objects.create(
            campaign=cls.campaign,
            client=cls.client_instance,
            price=0.05,
            date=1,
        )

    def test_campaign_impression_creation(self) -> None:
        self.assertIsInstance(self.impression, CampaignImpression)
        self.assertEqual(self.impression.price, 0.05)

    def test_unique_together_constraint(self) -> None:
        with self.assertRaises(ConflictError):
            CampaignImpression.objects.create(
                campaign=self.campaign,
                client=self.client_instance,
                price=0.05,
                date=1,
            )
