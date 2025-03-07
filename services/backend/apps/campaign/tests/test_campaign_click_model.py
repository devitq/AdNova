from django.core.cache import cache
from django.test import TestCase, override_settings

from apps.advertiser.models import Advertiser
from apps.campaign.models import Campaign, CampaignClick
from apps.client.models import Client
from config.errors import ConflictError


class CampaignClickModelTest(TestCase):
    @classmethod
    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def setUpTestData(cls) -> None:
        cache.set("current_date", 1)

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
        cls.click = CampaignClick.objects.create(
            campaign=cls.campaign,
            client=cls.client_instance,
            price=0.10,
            date=1,
        )

    def test_campaign_click_creation(self) -> None:
        self.assertIsInstance(self.click, CampaignClick)
        self.assertEqual(self.click.price, 0.10)

    def test_unique_together_constraint(self) -> None:
        with self.assertRaises(ConflictError):
            CampaignClick.objects.create(
                campaign=self.campaign,
                client=self.client_instance,
                price=0.10,
                date=1,
            )
