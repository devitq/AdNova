from uuid import uuid4

from django.test import TestCase, override_settings

from apps.advertiser.models import Advertiser
from apps.campaign.models import Campaign


class AdvertiserModelTest(TestCase):
    def setUp(self) -> None:
        self.advertiser = Advertiser.objects.create(name="Test Advertiser")

    def test_advertiser_creation(self) -> None:
        self.assertIsInstance(self.advertiser, Advertiser)
        self.assertEqual(self.advertiser.name, "Test Advertiser")

    def test_advertiser_str_method(self) -> None:
        self.assertEqual(str(self.advertiser), "Test Advertiser")

    def test_advertiser_id_property(self) -> None:
        self.assertEqual(self.advertiser.advertiser_id, self.advertiser.id)

        new_id = uuid4()
        self.advertiser.advertiser_id = new_id

        self.assertEqual(self.advertiser.id, new_id)

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def test_advertiser_campaigns_relationship(self) -> None:
        campaign = Campaign.objects.create(
            advertiser=self.advertiser,
            impressions_limit=0,
            clicks_limit=0,
            cost_per_impression=0,
            cost_per_click=0,
            ad_title="title",
            ad_text="text",
            start_date=15,
            end_date=16,
        )

        self.assertIn(campaign, self.advertiser.campaigns.all())
